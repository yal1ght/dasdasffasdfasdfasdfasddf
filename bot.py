import logging
import datetime
from fpdf import FPDF, XPos, YPos, Align
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Данные компании
COMPANY_INFO = {
    'representative': "Vadym Shevchenko, Manager",
    'address': "Dzielna 7, 00-154 Warsaw, Poland",
    'nip': "5279162645"
}

class ContractPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_margins(20, 20, 20)
        self.set_auto_page_break(True, 20)
        self.add_page()
        self.set_font("Helvetica", size=11)
    
    def header(self):
        if self.page_no() == 1:
            self.set_font("Helvetica", 'B', 16)
            self.cell(0, 10, "EUROLUXE Sp. z o.o.", 0, 1, 'C')
            self.ln(5)
    
    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", 'I', 8)
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, 'C')
    
    def add_section(self, title, content):
        self.set_font("Helvetica", 'B', 12)
        self.cell(0, 8, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font("Helvetica", '', 11)
        self.multi_cell(0, 6, content)
        self.ln(5)
    
    def add_key_value(self, key, value):
        line_height = 6
        self.set_font("Helvetica", 'B', 11)
        self.cell(60, line_height, f"{key}:", border=0)
        self.set_font("Helvetica", '', 11)
        self.cell(0, line_height, str(value), ln=1)


async def start(update: Update, context: CallbackContext) -> None:
    """Отправляет приветственное сообщение с инструкциями"""
    user = update.message.from_user
    logger.info("Пользователь %s начал чат.", user.first_name)
    
    await update.message.reply_text(
        f"Здравствуйте, {user.first_name}!\n"
        "Я помогу вам быстро сформировать договор на английском языке для клиента.\n\n"
        "Пожалуйста, введите данные клиента в следующем формате (каждое поле с новой строки):\n\n"
        "ФИО клиента\n"
        "Адрес клиента\n"
        "Телефон клиента\n"
        "Email клиента\n"
        "Страна назначения\n"
        "Дата начала тура (ДД.ММ.ГГГГ)\n"
        "Дата окончания тура (ДД.ММ.ГГГГ)\n"
        "Количество участников\n"
        "Транспорт (например, 'flight from Warsaw')\n"
        "Размещение (например, 'Hotel Marriott, double room')\n"
        "Стоимость (цифрами)\n"
        "Валюта (например, EUR, USD, PLN)\n\n"
        "Пример:\n"
        "John Smith\n"
        "123 Main St, New York\n"
        "+1 234 567 890\n"
        "john@example.com\n"
        "Italy\n"
        "15.08.2023\n"
        "25.08.2023\n"
        "2\n"
        "Flight from Warsaw to Rome\n"
        "Hotel Roma, double room\n"
        "2500\n"
        "EUR"
    )

def create_contract_pdf(contract_data):
    """Создает PDF файл с договором"""
    pdf = ContractPDF()
    
    # Заголовок договора
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(0, 10, "AGREEMENT FOR THE PROVISION OF TOURIST SERVICES", align=Align.C, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", '', 11)
    pdf.cell(0, 8, f"concluded on {contract_data['contract_date']} between:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(10)
    
    # Информация о компании
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 8, "Travel agency:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", '', 11)
    pdf.add_key_value("Name", "Euroluxe Sp. z o.o.")
    pdf.add_key_value("Address", COMPANY_INFO['address'])
    pdf.add_key_value("Tax ID (NIP)", COMPANY_INFO['nip'])
    pdf.add_key_value("Represented by", COMPANY_INFO['representative'])
    pdf.ln(5)
    
    # Информация о клиенте
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 8, "and the Client:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", '', 11)
    pdf.add_key_value("Full name", contract_data['client_name'])
    pdf.add_key_value("Residential address", contract_data['client_address'])
    pdf.add_key_value("Phone", contract_data['client_phone'])
    pdf.add_key_value("Email", contract_data['client_email'])
    pdf.ln(10)
    
    # §1. SUBJECT OF THE AGREEMENT
    pdf.add_section(
        "§1. SUBJECT OF THE AGREEMENT",
        "1. The subject of this agreement is the organization of a tourist trip with the following details:"
    )
    
    # Детали поездки
    trip_details = [
        ("Destination", contract_data['destination']),
        ("Date", f"from {contract_data['start_date']} to {contract_data['end_date']}"),
        ("Number of participants", contract_data['participants']),
        ("Means of transport", contract_data['transport']),
        ("Accommodation", contract_data['accommodation'])
    ]
    
    for key, value in trip_details:
        pdf.add_key_value(key, value)
    
    pdf.multi_cell(0, 6, "2. The detailed trip itinerary constitutes Annex No. 1 to this agreement.")
    pdf.ln(10)
    
    # §2. PRICE AND PAYMENT TERMS
    payment_terms = (
        f"1. The total price of the tourist trip is: {contract_data['price']} {contract_data['currency']}\n"
        "2. The price includes:\n"
        "   - transport\n"
        "   - accommodation\n"
        "   - meals\n"
        "   - care of a tour representative (resident)\n"
        "3. The Client agrees to transfer the full amount to the account provided by the company"
        "no later than 3 days after signing this agreement.\n"
        "4. In certain cases, due to technical or banking limitations (including transaction limits),"
        "our company reserves the right to provide multiple official accounts for processing the payment."
    )
    pdf.add_section("§2. PRICE AND PAYMENT TERMS", payment_terms)
    
    # §3. RIGHTS AND OBLIGATIONS OF THE PARTIES
    rights_obligations = (
        "1. The travel agency undertakes to properly provide the services as described.\n"
        "2. The Client agrees to comply with the rules and laws of the destination country.\n"
        "3. The Client has the right to:\n"
        "   - receive all necessary information prior to departure\n"
        "   - file a complaint\n"
        "   - transfer the agreement to another person (with the agency's consent)"
    )
    pdf.add_section("§3. RIGHTS AND OBLIGATIONS OF THE PARTIES", rights_obligations)
    
    # §4. TERMINATION AND CANCELLATION
    termination_text = (
        "1. The Client may withdraw from the agreement before the trip begins.\n"
        "2. The customer may cancel the trip no later than 3 days prior to departure.\n"
    )
    pdf.add_section("§4. TERMINATION AND CANCELLATION", termination_text)
    
    # §5. COMPLAINTS
    complaints_text = (
        "1. Complaints must be reported by residents in text format via Telegram messenger within 30 days.\n"
        "2. The travel agency must respond within 14 days."
    )
    pdf.add_section("§5. COMPLAINTS", complaints_text)
    
    # §6. INSURANCE AND GUARANTEE
    pdf.add_section("§6. INSURANCE AND GUARANTEE", 
                   "1. The Client is covered by basic accident and medical insurance (NNW and KL).")
    
    # §7. FINAL PROVISIONS
    final_provisions = (
        "1. Any matters not covered by this agreement shall be governed by the provisions of the Polish Civil Code and the Act on Tourist Events.\n"
        "2. The agreement was concluded electronically and sent to both parties by telegram messenger.\n"
        "3. The Client confirms that they have read and accept the terms of this agreement."
    )
    pdf.add_section("§7. FINAL PROVISIONS", final_provisions)
    
    # Подписи
    pdf.ln(15)
    col_width = (pdf.w - 40) / 2
    pdf.set_font("Helvetica", 'B', 11)
    pdf.cell(col_width, 8, "For and on behalf of Euroluxe Sp. z o.o.", new_x=XPos.RIGHT)
    pdf.cell(col_width, 8, "Client:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(15)
    
    pdf.cell(col_width, 8, "___________________________", new_x=XPos.RIGHT)
    pdf.cell(col_width, 8, "___________________________", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.set_font("Helvetica", '', 10)
    pdf.cell(col_width, 6, COMPANY_INFO['representative'], new_x=XPos.RIGHT)
    pdf.cell(col_width, 6, contract_data['client_name'], new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    # Сохраняем PDF
    filename = f"contract_{contract_data['client_name'].replace(' ', '_')}_{datetime.datetime.now().strftime('%Y%m%d%H%M')}.pdf"
    pdf.output(filename)
    return filename

async def handle_message(update: Update, context: CallbackContext) -> None:
    """Обрабатывает введенные пользователем данные и генерирует договор"""
    try:
        input_data = [line.strip() for line in update.message.text.split('\n') if line.strip()]
        if len(input_data) < 12:
            await update.message.reply_text("Недостаточно данных. Пожалуйста, введите все требуемые поля.")
            return
        
        contract_data = {
            'contract_date': datetime.datetime.now().strftime("%d.%m.%Y"),
            'client_name': input_data[0],
            'client_address': input_data[1],
            'client_phone': input_data[2],
            'client_email': input_data[3],
            'destination': input_data[4],
            'start_date': input_data[5],
            'end_date': input_data[6],
            'participants': input_data[7],
            'transport': input_data[8],
            'accommodation': input_data[9],
            'price': input_data[10],
            'currency': input_data[11],
        }
        
        # Создаем PDF
        filename = create_contract_pdf(contract_data)
        
        # Отправляем PDF пользователю
        with open(filename, 'rb') as document:
            await update.message.reply_document(
                document=document,
                caption="Ваш договор готов!",
                filename=f"Contract_{contract_data['client_name']}.pdf"
            )
        
        await update.message.reply_text("Договор успешно сформирован и отправлен в формате PDF!")
    
    except Exception as e:
        logger.error("Ошибка при формировании договора: %s", e)
        await update.message.reply_text("Произошла ошибка при обработке данных. Пожалуйста, проверьте формат ввода и попробуйте снова.")

def main() -> None:
    """Запускает бота"""
    # Удаляем конфликтующие пакеты
    import os
    os.system("pip uninstall -y PyFPDF pypdf pytz")
    os.system("pip install --upgrade fpdf2 python-telegram-bot")
    
    # Замените 'YOUR_BOT_TOKEN' на токен вашего бота
    application = Application.builder().token("7368858343:AAHuiW7x6ZXH5cFU8U0HN2mACHnn4Pf3pOs").build()
    
    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main()