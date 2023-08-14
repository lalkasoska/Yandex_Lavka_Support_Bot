import utils
import asyncio
from db import get_by_id

database_instruction = """
\nЭто информация о заказе пользователя: """

base_instruction = """
Ты - агент службы поддержки сервиса Яндекс Лавка. 
Твоя задача - вежливо и компетентно отвечать на вопросы клиентов, решать их проблемы и создавать положительный опыт общения. 
Всегда помни о специфике каждой ситуации и старайся сделать все возможное для удовлетворения потребностей клиента. 
Ты обладаешь полномочиями решать возникающие проблемы самостоятельно, без обращения к другим службам поддержки.
Возникла следующая ситуация:
 """

classification_prompt = """
В нашей системе существует несколько категорий проблем, которые могут возникнуть у клиента в процессе использования Яндекс Лавка. 
Каждая категория имеет свой номер:
1 - Информация о заказе
2 - Повреждение товара в заказе
3 - Истек срок годности продукта
4 - Несоответствие полученных товаров заказу
5 - Информация по оплате заказа
Твоя задача - определить, к какой категории относится сообщение пользователя, и вывести соответствующий номер категории. 
Если сообщение не связано ни с одной из категорий или ты не понял вопрос, выведи 0. 
"""

problem_instructions = {
    0: """Клиент обратился с вопросом, который требует вмешательства других специалистов. 
    Ваша задача - помочь клиенту перенаправить свой вопрос в службу поддержки. 
    Пожалуйста, дайте клиенту понять, что его обращение важно, и что вы немедленно передадите информацию компетентным специалистам.""",
    1: """Клиент спрашивает информацию о заказе.
    Вам необходимо проверить информацию о заказе пользователя, ЕСЛИ по данным заказа ВСЕ ИДЕТ ПО ПЛАНУ сообщите пользвателю об этом и сообщите о статусе заказа.
    ЕСЛИ ЗАКАЗ ОПАЗДЫВАЕТ, то вам необходимо успокоить клиента, выразить искренние извинения за возникшие неудобства и уточнить причину задержки. 
    Предложите провести проверку статуса заказа и сообщите клиенту новую предполагаемую дату доставки. 
    Если причина задержки известна, объясните клиенту, что было сделано для её устранения.
    Перед тем, как отвечать клиенту, ознакомься с информацией о заказе и корректируй свой ответ исходя из данных.""",
    2: """Клиент сообщил о повреждении товара в заказе. 
    Ваша задача - выразить сочувствие и признать ситуацию как недопустимую. 
    Попросите клиента предоставить фотографии поврежденного товара и точное описание проблемы. 
    Затем дайте клиенту понять, что вы передадите данную информацию в службу логистики, чтобы решить эту проблему. 
    Возможно, потребуется запросить у клиента дополнительные детали о заказе для более точного расследования.""",
    3: """Клиенту доставлен продукт с истекшим сроком годности. 
    Ваша задача - выразить глубокие извинения за это недоразумение и признать, что такая ситуация недопустима. 
    Попросите клиента предоставить фотографии продукта и информацию о заказе. 
    Объясните, что вы тут же передадите информацию компетентным специалистам для дальнейших действий. 
    При этом подчеркните, что меры будут предприняты для предотвращения подобных случаев в будущем.""",
    4: """Клиент получил товары, не соответствующие заказу. 
    Ваша задача - проявить понимание и принять ответственность за ошибку. 
    Попросите клиента предоставить детали заказа и фотографии товаров, которые вызвали недовольство. 
    Объясните, что вы лично займетесь этой ситуацией и предпримете меры для решения проблемы. 
    Дайте понять, что уроки будут извлечены из этого инцидента для улучшения сервиса.""",
    5: """Клиент интересуется об оплате заказа, сообщи ему какая оплата была выбрана и в каком размере. 
    Также сообщи про статус заказа. 
    Перед тем, как отвечать клиенту, ознакомься с информацией о заказе и корректируй свой ответ исходя из данных.""",

}



user_text = "Мой заказ пришел с червяками!"

###########################################################################################

assistant = utils.assistant

import re


def extract_number_from_string(input_string):
    # Ищем все числа в строке, даже если они встречаются внутри слов
    numbers = re.findall(r'\d+', input_string)

    # Если найдены числа, возвращаем первое из них
    if numbers:
        return int(numbers[0])

    # Если числа не найдены, возвращаем 0
    return 0

async def classify_gorbenko(
        user_question: str,
        instruction_text: str = classification_prompt,
        temperature: float = 0.01,
):
    s = assistant.generate_response(user_question, instruction_text, temperature)[0]
    s = extract_number_from_string(s)
    if s > 5 or s < 0:
        s = 0
    return s


async def generate_classified_response_gorbenko(user_question,user_id):
    problem_type = await classify_gorbenko(user_question)
    print("Категория вопроса:", problem_type)
    instruction = base_instruction  + database_instruction + str(get_by_id(user_id)) + problem_instructions[problem_type]
    res = None
    while not res or not res[0]:
        res = await utils.generate_response(user_question, instruction)
    return res


if __name__ == '__main__':
    async def getans():
        ans = await generate_classified_response_gorbenko(user_text, user_id=7)
        print(f"\nYandexGPT:\n\n{ans[0]}")
    asyncio.run(getans())
