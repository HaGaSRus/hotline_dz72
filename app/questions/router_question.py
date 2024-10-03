import traceback
import html
from typing import List
from fastapi_versioning import version
from fastapi import APIRouter, Depends, Path, Query, HTTPException, status
from fastapi_pagination import Page, paginate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from app.admin.pagination_and_filtration import CustomParams
from app.dao.dependencies import get_current_admin_or_moderator_user
from app.database import get_db, async_session_maker
from app.exceptions import QuestionNotFound, ErrorInGetQuestions, \
    ErrorInGetQuestionWithSubquestions
from app.logger.logger import logger
from app.questions.dao_queestion import build_question_response, QuestionService, get_sub_questions, \
    build_subquestions_hierarchy, build_subquestion_response
from app.questions.models import Question, SubQuestion
from app.questions.schemas import QuestionResponse, QuestionCreate, DeleteQuestionRequest
from pydantic import ValidationError
import asyncio
from sqlalchemy import func

router_question = APIRouter(
    prefix="/question",
    tags=["Вопросы"],
)


# Эндпоинт для получения всех вопросов с вложенными под-вопросами

@router_question.get("/all-questions", response_model=List[QuestionResponse])
@version(1)
async def get_questions(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Question))
        questions = result.scalars().all()

        logger.info(f"Найденные вопросы: {[q.id for q in questions]}")  # Логируем найденные вопросы

        tasks = [get_sub_questions(db, question.id) for question in questions]
        sub_questions_list = await asyncio.gather(*tasks)

        logger.info(f"Найденные под-вопросы: {sub_questions_list}")  # Логируем найденные под-вопросы

        question_responses = []
        for question, sub_questions in zip(questions, sub_questions_list):
            hierarchical_sub_questions = build_subquestions_hierarchy(sub_questions)

            question_response = QuestionResponse(
                id=question.id,
                text=question.text,
                category_id=question.category_id,
                subcategory_id=question.subcategory_id,
                answer=question.answer,
                number=question.number,
                depth=question.depth,
                count=question.count,
                parent_question_id=question.parent_question_id,
                sub_questions=hierarchical_sub_questions
            )
            question_responses.append(question_response)

        return question_responses
    except Exception as e:
        logger.error(f"Ошибка в get_questions: {e}")
        raise ErrorInGetQuestions(detail=str(e))


@router_question.get("/{question_id}", response_model=QuestionResponse)
@version(1)
async def get_question_with_subquestions(
        question_id: int,
        db: AsyncSession = Depends(get_db)
):
    try:
        # Получаем вопрос по ID
        question = await db.get(Question, question_id)
        if not question:
            raise QuestionNotFound

        # Получаем все подвопросы
        sub_questions = await get_sub_questions(db, question_id)

        # Формируем иерархию под-вопросов
        hierarchical_sub_questions = build_subquestions_hierarchy(sub_questions)

        # Формируем ответ с иерархией
        question_response = QuestionResponse(
            id=question.id,
            text=question.text,
            category_id=question.category_id,
            subcategory_id=question.subcategory_id,
            answer=question.answer,
            depth=question.depth,
            number=question.number,
            count=question.count,
            parent_question_id=question.parent_question_id,
            sub_questions=hierarchical_sub_questions  # Используем уже построенную иерархию
        )

        return question_response
    except Exception as e:
        logger.error(f"Ошибка в get_question_with_subquestions: {e}")
        raise ErrorInGetQuestionWithSubquestions(detail=str(e))


@router_question.get("/pagination-questions",
                     status_code=status.HTTP_200_OK,
                     response_model=Page[QuestionResponse],
                     summary="Отображение всех вопросов верхнего уровня с пагинацией")
@version(1)
async def get_all_questions(params: CustomParams = Depends()):
    """Получение всех вопросов верхнего уровня. С пагинацией"""
    try:
        async with async_session_maker() as session:
            # Получаем только вопросы верхнего уровня (где parent_question_id = None)
            stmt = select(Question).filter(Question.parent_question_id.is_(None)).options(
                selectinload(Question.sub_questions))
            result = await session.execute(stmt)
            question_all = result.scalars().all()

        # Преобразуем вопросы в нужный формат ответа
        question_responses = [
            QuestionResponse(
                id=question.id,
                text=question.text,
                category_id=question.category_id,
                subcategory_id=question.subcategory_id,
                answer=question.answer,
                number=question.number,
                depth=question.depth,
                count=question.count,
                parent_question_id=question.parent_question_id,
                sub_questions=[],
            )
            for question in question_all
        ]

        # Применение кастомных параметров пагинации
        return paginate(question_responses, params=params)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# Роут для создания вопроса или под вопроса
@router_question.post("/create", summary="Создание вопроса или подвопроса")
@version(1)
async def create_question(
        question: QuestionCreate,
        db: AsyncSession = Depends(get_db),
        current_user=Depends(get_current_admin_or_moderator_user)
):
    try:
        logger.info("Создание нового вопроса с текстом: %s", question.text)

        if question.is_subquestion:
            if not question.parent_question_id:
                raise HTTPException(status_code=400, detail="Для подвопроса нужно указать parent_id")

            # Создаем подвопрос
            new_question = await QuestionService.create_subquestion(
                question=question,
                db=db
            )
            response = await build_subquestion_response(new_question)  # Изменение здесь
            logger.info(f"Создание подвопроса для родительского вопроса с ID: {question.parent_question_id}")
        else:
            # Создаем родительский вопрос
            new_question = await QuestionService.create_question(
                question=question,
                category_id=question.category_id,
                db=db
            )
            response = await build_question_response(new_question)  # Оставляем как есть
            logger.info("Создание родительского вопроса")

        # Возвращаем ответ
        logger.info("Вопрос успешно создан: %s", response)
        return response

    except ValidationError as ve:
        logger.error(f"Ошибка валидации данных ответа: {ve}")
        raise HTTPException(status_code=422, detail=f"Validation error: {ve.errors()}")
    except IntegrityError as e:
        await db.rollback()
        logger.error("IntegrityError при создании вопроса: %s", e)
        raise HTTPException(status_code=409, detail="Ошибка целостности данных: возможно, такой вопрос уже существует.")
    except Exception as e:
        logger.error("Ошибка при создании вопроса: %s", e)
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Не удалось создать вопрос")


@router_question.post("/delete", summary="Удаление вопроса или под-вопроса")
@version(1)
async def delete_question(
        delete_request: DeleteQuestionRequest,
        db: AsyncSession = Depends(get_db),
        current_user=Depends(get_current_admin_or_moderator_user)
):
    """Удаление вопроса или под-вопроса по ID, если у него нет вложенных под-вопросов"""
    try:
        # Извлекаем ID основного вопроса и под-вопроса
        id_to_delete = delete_request.sub_question_id
        main_question_id = delete_request.question_id

        if id_to_delete > 0:  # Удаляем под-вопрос, если он указан
            # Удаляем под-вопрос
            sub_question = await db.get(SubQuestion, id_to_delete)
            if not sub_question:
                raise HTTPException(status_code=404, detail="Под-вопрос не найден")
            # Проверяем, принадлежит ли под-вопрос основному вопросу
            if sub_question.parent_question_id != main_question_id:
                raise HTTPException(status_code=400, detail="Под-вопрос не принадлежит указанному основному вопросу")
            # Проверяем наличие вложенных под-вопросов в базе данных
            sub_questions_count = await db.execute(select(func.count()).where(SubQuestion.parent_subquestion_id == id_to_delete))
            if sub_questions_count.scalar() > 0:
                raise HTTPException(status_code=400, detail="Невозможно удалить под-вопрос с вложенными под-вопросами")
            # Удаляем под-вопрос
            await db.delete(sub_question)
        else:  # Удаляем основной вопрос, если sub_question_id не указан или равен 0
            # Удаляем основной вопрос
            question = await db.get(Question, main_question_id)
            if not question:
                raise HTTPException(status_code=404, detail="Вопрос не найден")
            # Проверяем наличие под-вопросов у основного вопроса
            question_sub_questions_count = await db.execute(select(func.count()).where(SubQuestion.parent_question_id == main_question_id))
            if question_sub_questions_count.scalar() > 0:
                raise HTTPException(status_code=400, detail="Невозможно удалить вопрос с под-вопросами")
            # Удаляем основной вопрос
            await db.delete(question)

        await db.commit()
        return {"detail": "Вопрос или под-вопрос успешно удалены"}
    except Exception as e:
        await db.rollback()
        logger.error(f"Ошибка при удалении вопроса: {e}")
        raise HTTPException(status_code=400, detail="Ошибка при удалении вопроса")



@router_question.post("/update/{question_id}", response_model=QuestionResponse, summary="Обновление вопроса")
@version(1)
async def update_question(
        question_data: QuestionCreate,
        question_id: int = Path(..., ge=1),
        db: AsyncSession = Depends(get_db),
        current_user=Depends(get_current_admin_or_moderator_user)
):
    """Обновление вопроса и его под-вопросов по ID"""
    try:
        # Получаем основной вопрос
        question = await db.get(Question, question_id)
        if not question:
            raise HTTPException(status_code=404, detail="Вопрос не найден")

        # Обновляем поля основного вопроса
        for key, value in question_data.dict(exclude_unset=True).items():
            setattr(question, key, value)

        # Обрабатываем вложенные вопросы, если они есть
        if 'subquestions' in question_data.dict(exclude_unset=True):
            subquestions_data = question_data.dict()['subquestions']
            for subquestion_data in subquestions_data:
                subquestion_id = subquestion_data.get('id')
                if subquestion_id:
                    # Получаем под-вопрос по ID
                    subquestion = await db.get(SubQuestion, subquestion_id)
                    if not subquestion:
                        raise HTTPException(status_code=404, detail=f"Под-вопрос с ID {subquestion_id} не найден")

                    # Обновляем поля под-вопроса
                    for key, value in subquestion_data.items():
                        setattr(subquestion, key, value)
                else:
                    # Если ID нет, можно создать новый под-вопрос
                    new_subquestion = SubQuestion(**subquestion_data)
                    db.add(new_subquestion)

        # Сохраняем изменения
        await db.commit()

        # Возвращаем обновленный вопрос
        return QuestionResponse.model_validate(question)
    except Exception as e:
        await db.rollback()
        logger.error(f"Ошибка при обновлении вопроса: {e}")
        raise HTTPException(status_code=400, detail=str(e))
