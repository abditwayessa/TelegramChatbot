import json
import logging
from turtle import update
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext
from fuzzywuzzy import fuzz, process
from telegram import Bot
from datetime import datetime
import pytz
import re


# from models import User, UserMessage, engine
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Logging setup
# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logging.basicConfig(
    filename="log.txt",
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Fetch environment variables
# SUPABASE_DATABASE_URL = os.getenv('SUPABASE_DATABASE_URL')
TOKEN = os.getenv('TOKEN')
ADMIN_USER = os.getenv('ADMIN_USER')
USER_DATA_FILE = "users.json"
ATM_DATA_FILE = "atm.json"
BRANCH_DATA_FILE = "branch.json"
BROADCAST_FILE = "broadcast.json"
# Let's try to open the user file
try:
    with open(USER_DATA_FILE, 'r') as file:
        user_data = json.load(file)
except FileNotFoundError:
    user_data = {}

#let try broadcast
try:
    with open(BROADCAST_FILE, 'r') as file:
        broadcast_data = json.load(file)
except FileNotFoundError:
        broadcast_data = {}

#let's load broadcast data
def load_broadcast_data():
    with open(BROADCAST_FILE, 'r') as file:
        data = json.load(file)
        return data['broadcasted']
broadcasted_data = load_broadcast_data()

# let's try to open atm file
def load_atm_data():
    with open(ATM_DATA_FILE, 'r') as file:
        data = json.load(file)
        return data['atms']
atms = load_atm_data()

# branch file
def load_branch_data():
    with open(BRANCH_DATA_FILE, 'r') as file:
        data = json.load(file)
        return data['branchs']
branchs = load_branch_data()
# normalized_atm = {branch.lower().replace(" ", "_"): branch for branch in atms}


def save_user_data():
    with open(USER_DATA_FILE, 'w') as file:
        json.dump(user_data, file, indent=2)

def read_user_data(user_id):
    try:
        with open(USER_DATA_FILE, 'r') as file:
            user_data = json.load(file)
        username = user_data.get(user_id)
        # logger.info(f"username : "+ username)
        if username == None:
            username='username+en'
            return username
        else:
            return username
    except FileNotFoundError:
        logger.info(f"User data file not found.")
        return "Not found"
    except json.JSONDecodeError:
        print("Error decoding JSON.")
        return "Error"

def log_interaction(update):
    user_info = ""

    if update.message:
        user = update.message.from_user
        user_info = f"User {user.username or 'Unknown'} (ID: {user.id}) - Command: {update.message.text}"

    elif update.callback_query:
        user = update.callback_query.from_user
        user_info = f"User {user.username or 'Unknown'} (ID: {user.id}) - Callback Data: {update.callback_query.data}"

    logger.info(user_info)

timezone = pytz.timezone("Africa/Nairobi")
current_time = datetime.now(timezone)
formatted_time = current_time.strftime("%Y-%m-%d %I:%M %p")

bot = Bot(token=TOKEN)
admin_user = ADMIN_USER
try:
    bot.send_message(chat_id=admin_user, text="Bot is started @ "+formatted_time)
    # Your bot code here
except Exception as e:
    bot.send_message(chat_id=admin_user, text=f"Bot has stopped due to an error: {e} @ {formatted_time}")
# Session = sessionmaker(bind=engine)
# session = Session()
# My global Variables
lang_id = 0
lang_to_save = 0
lang_perf = ''
lang_faq = ''
user_id_global = ''
username_global = ''
# Predefined FAQ
faq_list = ["Registration", "Digital bank access locked", "Reset Password", "Transfer Issue", "Sign in Option", "Digital Bank suspended", "Password field is not work on registration","Fraud Protection", "Coop App Security", "What is Coop App?", "Why Coop App?","Bill Payment","Coopay-ebirr vs. Coop App", "Coopbank IFB platform"]
faq_list_oro = ["Akkaataa Galmee", "Tajaajilli baankii diijitaalaa cufame", "Jecha-darbiin dagatame jijjiiruu", "Qarshiin baankii biraatti ergee naaf hin dhaqabne", "Filannoo Seensaa", "Tajaajilli baankii diijitaalaa adda kutuu", "Yeroo galmee jecha-darbii fudhachuu dide","Gowwomsaa irraa of eeguu", "Nageenyummaa Coop App", "Coop App Maalii?","Coop App maaliif filatama?","Kaffaltii Biilii","Coopay-ebirr fi Coop App","Coopbank IFB platform"]
# faq_list_am = ["ምዝገባ", "ዲጂታል ባንክ ተቆልፏል","የተረሳ የይለፍ ቃል", "የዝውውር ጉዳይ", "የመግባት አማራጮች", "የእኔ ዲጂታል ባንኪንግ ተሰናክሏል", "ርሰት ፓሥዎርድ ", "የማጭበርበር ጥበቃ", "ኩፕ አፕ ደህንነት", "Coop App ምንድን ነው?","ኩፕ አፕ ለምን?" ]
faq_list_am = ["ምዝገባ", "ዲጂታል ባንክ ተቆልፏል","የተረሳ የይለፍ ቃል", "የዝውውር ጉዳይ", "ግመግባት አማራጮች",  "ዲሰብልድ ኩፕ አፕ", "ርሰት ፓሥዎርድ ","ፓሥዎርድ መስክ አይሰራም  ", "የማጭበርበር ጥበቃ", "ኩፕ አፕ ደህንነት", "Coop App ምንድን ነው?","ኩፕ አፕ ለምን?" ,"ቢል መክፈል","Coopay-ebirr እና Coop App","ከወለድ ነፃ ፕላትፎርም"]
# Predefined Q&A pairs
qa_pairs_en = {
    "How to register on coop app service for personal use? registration how to register coopapp Coop App Retail Registratio": "Coop App Retail Registration\n\n1. To register first you must hold coop bank account\n 2. Install the application from play store or app store\n 3. Open the application\n 4. Select Register/Activate\n 5. Select Retail Banking\n 6. Select Register Now\n 7. Enter Account number and Captcha\n 8. Select activate now. \n 9. Enter the activation ID and code sent via SMS\n 10.  Enter username (Min 8 characters) then check availability.\n11. Enter password (Min 8 alphanumeric characters).",
    "Digital banking access locked": " Digital banking access locked\n\n While you try wrong password for more than five times for 3 minutes your digital banking access will be locked.\n Try after 3 minute by changing your password.",
    "How to reset password? forgotten password": " Reset password\n\nStep 1:- on login screen click on  can\'t sign in button\nStep 2:- select retail banking\nStep 3:-on the first field enter your account number and on the second field enter the captcha then click continue button\nStep 4:-you will get you username and there is reset my password button and click it\nStep 5:- you will get OTP on SMS , so you will enter the OTP and click next\nStep 6:- you will get the field to enter your new password and reenter your password on the second field and click continue button ",
    "My password is expired. How to fix it?": "Expired password\n\nStep 1:- Open the app or web link and click on  Can\'t sign in?\nStep 2:- Select Retail banking\nStep 3:- On the first field enter your account number and on the second field enter the captcha then click Continue button\nStep 4:- You will get you username and there is reset my password option then click it.\nStep 5:- You will get OTP on SMS , so you will enter the OTP on provided field and click Next\nStep 6:- You will get the field to enter your new password and re-enter your password on the second field enter strong password that must have capital letter, small letter, special symbol and number and click Continue button.",
    "I transferred money to other bank, but not yet credited. other bank transfer issue": " Other bank issue\n\n It will be refunded to your account within short period time. Until it will be refunded have patience!",
    "What are the sign in options available for the coop app service?": "Coop App sign in option\n\n There are 3 sign in option\n\t1.    Username and Password\n\t2. PIN\n\t3.   Biometrics(Facial Recognition(Face ID) or Fingerprint",
    "My digital banking accessibility is disabled. How I gain access it again? suspended mobile bank": "Solution for suspended user\n\n Visit your nearest branch with ID in your hand. They fill Coop App Service Management form with checked enable digital bank.",
    "During onboarding doesn't take password after we enter username. password field is not working on registration": "Doesn\'t take password\n\n After your input your username click Check Availability under username field. If it displays 'Username is available' and now you can enter your password. But if it says 'Username is not available' username you entered is already taken by another user so use another.",
    "How I protect my self from frauds? fraud steal fraud protection prevent froud":"Protect from fraudsters\n\n1. Lock your SIM card with a PIN Code. \n2. Instead of using the pattern on your screen lock, try to use PIN or Password. \n3. Use with caution in public areas. \n4. Always log out of your mobile banking app when you are done using it. \n5. Regularly monitor your account activity and immediately report any suspicious transactions to the bank. \n6. Change your password regularly.",
    "Coop Apps Security Security":"Coop App Security\n\nCoop App is secured with state-of-the-art technology, including advanced encryption and multi-layered protection, ensuring your data always stays safe.",
    "What is Coop App? Coop App What is Coopapp":"What is Coop App\n\nThe Coop App is an omnichannel digital banking platform designed to provide seamless and integrated banking experiences across multiple channels. Whether through mobile devices or web interfaces, the Coop App ensures that customers can manage their finances effortlessly from anywhere, at any time.",
    "Why Coop App? Importance of Coop App why Coopapp importance of CoopApp":"Why Coop App?\n\n1. Effeciency\n2. Diversified(hybird)\n3. Uiformity\n4. Security\n5. Accessibility\n6. Insight",
    "Can I pay my bills through? Bill Payment":"Possible to pay my Bill?\n\nYou Can pay bill of Ethiopian Airlines, Canal+, DSTV and etc.",
    "I need help with my account. Can I speak to a representative? account problem":"Use call center \n\nYes, You can. You can also use our call center 609.",
    "How do I report a problem with my banking app? mobile banking problem":"Mobile Bank Problem\n\nYou can report at branch or through call center(609).",
    "What\'s make Coopapp different from others platforms? Coop app different other bank and Coopapp":"What makes Coop App Different\n\nCoop App is differe from other digital banking starting from is developement environment to service provided through this plaftorm. Coop App have two major modules which are Retail Banking and Business Banking. It has it\'s own other bank and Coopbank beneficiary  management, Schedule transfer,Repeat Transfer, Bulk Transfer(Business banking Feature), Branch and ATM locator filtering by service they provide and distance, Account preview(User preference) and etc.",
    "What security measures are in place? Does it offer multi-factor authentication? 2FA":"Security Measure\n\nEvery time you login we check if you are who you said using OTP mechanism. While you Login the system will send you an OTP and the app will insert the OTP by it self. If you want more about Coop App Security just type `Coop Apps Security`",
    "What are the transaction limits for transfers? transfer limit":"Transfer Limit\n\nThe bank can set both daily and aggregate transaction limits, taking into account various factors such as compliance with financial regulations, customer requirements, internal situation and operational flexibility.",
    "What features does the mobile banking product offer? Features ":"Coop App Features\n\nRetail Banking\n-Transfer(Own account transfer, transfer to other person, Wallet transfer, both Coopbank and other bank beneficiary management, schedule transfer, repeat transfer, one-time transfer and etc.)\n-Account(You can access your all Coopbank account, account detail, account filter, transaction activities and search, transaction detail, dispute management and etc.)\n-Personalization(You can use 2 local language and English, account balance preview, reset credential, branch and ATM locator)\n-Bill Payment(one-time-bill payment and bill management)\n\nBusiness Banking(All retail banking feature and feature listed below)\n-User management\n-Approval Matrix\n-Bulk Transfer\n-Approval, Request and etc.",
    "How do I file a dispute for a wrong transaction?":"Wrong Transaction Issue\n\nOpen the transaction detail. Click Dispute transaction. Select Reason of the dispute. Type description and click Continue.",
    "Can I check my loan available balance? loan balance":"Loan Available Balance\n\nYes, From dasboard select your loan account and click info icon found on top right corner of the screen.",
    "How can I provide feedback on your services? feedback comment":"Feeback\n\nYou can provide your feedback through Coop App. Click menu button found top left corner click Messages and click + sign select area of your feedback and type your feedack or attach a file and send it.",
    "Retail Vs. Business Banking Service? difference of retail banking and business banking":"Retail Vs. Business Banking\n\nBusiness\nBusiness banking enables business customers to interact with their financial seamlessly across multiple channels, helping businesses to simplify their financial management processes and ultimately achieve operational excellence.\nRetail Banking\nLeverages the latest technologies  to create personalized, seamless experiences for customers across various digital touchpoints. Offer services such as online, mobile apps, which cater to the convenience of customers, access to information, and transactional services anytime, anywhere.",
    "Difference of Coopayebirr and Coop App? coopay-ebirr coopay ebirr":"Coopay-ebirr vs. Coop App\n\nCoop App is an Omnichannel platform while Coopay-ebirr is cross channel. In Coop App Conventional and IFB customers use separate channels and this segmentation is not found in Coopay-Ebirr. Using Coop App you can access all of your account including Loan account, on Coopay-ebirr you can access only one single account.",
    "Does Coop App have IFB platform? Interest free banking platform":"Coop App Ahuda(IFB)\n\nYes, Coop App Alhuda is separated app provided for our IFB account holders.",
    "Eligible document for business customer criteria business banking criteria":"Business Banking Eligibility\n\nBusiness Registration Documents:\n-Certificate of Incorporation (for corporations)\n-Business Registration Certificate (for sole proprietors/partnerships)\n-Memorandum and Articles of Association (for companies or associations)\nLetter from business entity:\n-If the business entity possesses the authority to manage its signatories or users, the letter from the business entity should include only the necessary information for the General Manager (Administrator).\n-If signatory or user management is overseen by a Coopbank branch, the business entity letter must incorporate the required information for all signatories.\nValid and renewed business license.\nValid and renewed signatory\'s identification documents.\nBoard Resolution or general assembly minute\nThe official application form provided by the bank, fully completed, signed and stamped.",
    "Check balance before log in to the app account preview":"Account Preview\n\n Account Preview is a feature that helps to see your available balance without sign-in. This option is off by default. If you want to try this feature you can On it from Settings.",
    "how to register business customer onboard business customer":"Business Banking Registration\n\nTo register for this service please visit your nearest branch.",
    "Network 2G 3G 4G 5G":"Network Related\n\nCoop App work on 3G, 4G or 5G.",
    "How can I use it Usage Coop App usage":"Coop App Usage\n\nFirst, register and activate your account effortlessly, no matter where you are. Once you sign in, you will have access to all your account details in one convenient place, allowing you to enjoy seamless and hassle-free transactions.",
    "your device is not compatible with this version device compatibility Device":"Device compatability\n\nCoop App works on Android above 9.0",
    "Coop App is not working for me is no working Coop App Status":"Coop App Status\n\n Please update your Coop App from App Store or Play Store. If the issue is not resolved call us on 609.",
    "Send my account number ":"Please visit your nearest branch.",
    "App is not working not work Coop App not work":"Please contact call center 609",
    "how can i activate my account how to activate Coop App coop app activation":"Coop App Activation\n\n To activate the Coop App, first register, and the system will send you an Activation ID and Activation Code. Enter these in the provided fields and create your username and password.",
    "Web is not working for me web link not work web access":"Web Access\n\n If you want to get web access please visit the nearest branch.",
    "Account missing missed ":"Missed Account\n\n If your account is not displayed on the dashboard please visit your nearest branch to add your account to the service"
}

qa_pairs_oro = {
    "Akkamitti Coop App galmaa\'u dandeenya? galmee register gochuu Akkaataa Galmee": "Akkataa \' Coop App\' itti galmaa\'an.\n\n1. Galmaa\'uuf jalqaba herregaa bankii keenyaa qabaachuu qabdu.\n 2. App \'Coop App\' playstore ykn AppStore irraa install godhadhaa.\n 3. App kana banaa\n 4. \'Register/Activate\' kan jedhu cuqaasaa. \n 5. \'Retail Banking \' kan jedhu filadhaa.\n 6. \'Register now\' kan jedhu filadhaa. \n 7. Lakk. herregaa keessaniif \'Captcha\' achirra jiru sana galachaa. \n 8. \'Activate Now\' kan jedhu filadhaa. \n 9. Gama lakk. bilbilaa keessaniif \'Activation ID\' fi \'Activation Code\' isiniif ergame iddoo, iddoo isatti galchuun \'Verify\' kan jettu cuqaasaa.\n 10. \'Username\'(Yoo xiqqaatee 8 kan guutuu) barbaaddaan galchuun \'Check Availability\' kan jettu tuquun \'Username\' kun nama biraan akka hin qabamne ilaalaa. Yeroo kana yoo \'Username is available\' isiniin jedhee namni fayyadama jiru waan hin jirreef tarkaanffii itti aanuutti darbaa. Yoo \'Username is not available\' isiinin jedhe garuu jijjiiruutuu isin irraa eegama.\n 11. Jecha darbii(Password) jabaa ta\'e kan qubee gurguddaa, qubee xixxiqqaa, lakkofsaaf mallattoo(symbol) of keessaa qabu bakka lamaanittuu galchuun \'Continue\' kan jettu cuqaasaa.\n 12. Amma fayyadamaa tajaajila \'Coop App\' taatanittu.   ",
    "\'Access locked\' naan jedha maal gochuutuu narraa eegama? digita banking access locked Tajaajilli baankii diijitaalaa cufame": "Furmaata \'Digital Banking Access Lock\' \n\nYeroo 5f isaa ol jecha darbii(password) sirrii hin taaneen yeroo yaaltan daqiiqaa 3f tajaajila kana fayyadamuu hin dandeessan. Yoo jecha darbii keessan dagattanii \'Can\'t Sign In?\' kan jettu fayyadamuun jijjiirachuun daqiiqaa 3 boodaa irra deebiin seenaa. ",
    "Tajaajila kanatti yeroon fayyadamuu ittin seenuuf filannoo akkamiin qaba? sign in option ashaaraa pin":"Tajaajila kana fayyadamuuf eenyummaakee adda baasuun akka inni si seensisuuf maloota 3 fayyadamuu dandeessa.\n 1. \'Username\' fi jecha darbii(password) fayyadamuun.\n 2. \'PIN\' fayyadamuun.\n 3.\'Biometrics\' jechuun \'Face ID\' ykn Ashaaraa qubaa \'Finger Print\' fayyadamuun.",
    "Jecha darbii(Password) dagatame akkamiin jijjiiruu dandeenya.reset password rest password can\'t sign in not sign":"Jecha darbii(password) dagatame jijjiiruu\n\n 1. App ykn marsariiti(web) banuun \'Can\'t Sing In?\' cuqaasaa.\n 2. \'Retail Banking\' kan jedhu filadhaa.\n 3. Tarree jalqabaa irratti lakk. herregaa galchuun kan lamaffaa irrattimmoo barreefama bakka lakk. herregaa galchitan jalatti argamuu jechun \'Captcha\' galchaa. Sana booda \'Continue\' kan jettu cuqasaa.\n 4. \'Username\' kessaan isiniif fida; sana booda \'Reset my password\' kan jedhu filadhaa.\n 5. Lakk. dijiitii 6 qabu gama lakk. bilbilaa keessaniin isiinif ergama. Lakk kana galchuun \'Next\' godhaa.\n 6. Jecha darbii(Password) jabaa ta'e galchuun \'Continue\' kan jettu cuqaasaa.",
    "Jechi iccitii koo yeroon isaa darbe. Akkamittin sirreessuu danda\'aa? change expired password":"Jecha darbii(password) yeroon itti darbe jijjiiruu\n\n 1. App ykn marsariiti(web) banuun \'Can\'t Sing In?\' cuqaasaa.\n 2. \'Retail Banking\' kan jedhu filadhaa.\n 3. Tarree jalqabaa irratti lakk. herregaa galchuun kan lamaffaa irrattimmoo barreefama bakka lakk. herregaa galchitan jalatti argamuu jechun \'Captcha\' galchaa. Sana booda \'Continue\' kan jettu cuqasaa.\n 4. \'Username\' kessaan isiniif fida; sana booda \'Reset my password\' kan jedhu filadhaa.\n 5. Lakk. dijiitii 6 qabu gama lakk. bilbilaa keessaniin isiinif ergama. Lakk kana galchuun \'Next\' godhaa.\n 6. Jecha darbii(Password) jabaa ta'e galchuun \'Continue\' kan jettu cuqaasaa.",
    "Maallaqa gara baankii biraatti ergee naaf hin dhaqabne. Other bank issue transfer to other bank Qarshiin baankii biraatti ergee naaf hin dhaqabne":"Maallaqa baankii biraatti ergamee\n\n Maallaqa gara baankii biratti ergitanii dafee isiniif qaqqabuu yoo dide maallaqi keessan yeroo muraasa giddutti gara herrega irra dabarfameetti deebii taa\'a.",
    "Coop App koo suspend suspended disabled deactivated ta\'e":"Fayyadamaa suspended ta'eef\n\nDamee isinitti dhiyoo jiru waraqaa eenyummaa keessan qabachuun deema. Unka \'Coop App Service Management\' jedhu bakka \' Digital Banking Access:\' jettu fuuldura \'Enable\' kan jettu keessatti mallattoo godhaa",
    "Akkamittii tajaajila kana addaan kutuu dandeenya? suspend deactive Tajaajilli baankii diijitaalaa uggurame":"Tajaajila addan kutuu\n\nTajaajila kana addaan kutuuf dirqama gara dame deemuun isin hin barbaachisuu. App ykn Marsariitii(Web) fayyadamuun adda kutuu dandeessu.\n 1. \'Username\' fi jecha darbii(password) keessan galchuun seenaa. \n 2. \'Menu\' cuqasuun Qindaa\'ina(Setting) filachuun \'Digital banking access\' kan jedhu filadhaa.\n 3. Filannoo jiran keesaa \'Off \' filachuun adda kutuu dandeessu",
    "Erga \'Username\' galchinee boodaa bakki jecha darbii(password) hin hojjetu.":"Password nuun fudhatu\n\nErga \'Username\' galchitanii boodaa \'Check Availability\' kan jettu cuqaasuun \'Username\' isin galchitan namni bira fayyadamaa jirachuu isaa jalqaba adda baasaa. Yoo \'Username\' isin galchitan fayyadamaan kan biraa fayyadamaa hin jiru ta'ee ofii isaa bakki jecha darbii(password) itti guutan ni banama.",
    "Gowwomsaa irraa of eeguu hanna hattuu irra of eeguu":"Gowwoomsitoota irraa of eeguuf \n1. SIM kaardii keessan PIN\'dhaan cufaa. \n2. Cuftuu bilbila keessaniif Paatternii fayyadamu irra PIN ykn Jecha-darbii(Password) fayyadamaa. \n3. Bakka namoonni baay\'een itti baay\'atutti of eeggannoodhaan fayyadamaa. \n4. Yeroo hunda Moobayil baankii fayyadamtanii xumurtan keessaa baha(sign out) godhaa. \n5. Sochii herrega keessanii yeroo yeroon hordofuu fi waanta shakkisiisaa ta\'e hatattamaan baankiidhaaf gabaasaa. \n6. Yeroo hunda jecha iccitii keessan jijjiira.",
    "Nageenyummaa Coop App Nageenya Coop Apps":"Nageenyummaa Coop App\n\nCoop App teknooloojii ammayyaatiin kan eegame yoo ta\'u, iccitii sadarkaa olaanaa fi eegumsa dachaa hedduu dabalatee, daataan keessan yeroo hunda nageenyumman isaa kan eegamedha.",
    "Coop App Maali?":"Coop App maali?\n\nCoop App waltajjii baankii dijitaalaa \'omnichannel\' kan tajaajila baankii mijataa, walitti fufaa fi walitti hidhama qabu karaa hedduu ta\'een kennuudhaaf qophaa\'eedha. Karaa moobaayilaa ykn marsaritii(website), Coop App maamiltoonni bakka kamirraayyuu, yeroo kamiyyuu faayinaansii isaanii dadhabbii malee hoogganuu danda\'u.",
    "Coop App maaliif filatama? malif filatama":"Coop App maaliif filatama?\n\n1. Qisaasama kan hir\'ise.\n2. Hunda kan hammate.\n3. Bakka hundatti walfakkaata.\n4. Nageenyumman isaa kan eegame.\n5. Dhaqqabummaa kan qabu.\n6. Waan hunda kan argisiisu.",
    "Kaffaltii Biilii kaffaluu nan dandaa\'aa? Bill Payment":"Kaffaltii Biilii\n\nKaffaltii Daandii Qilleensaa Itoophiyaa, Canal+, DSTV fi kkf kaffaluun ni danda\'ama.",
    "Herregakoo irratti gargaarsa na barbaachisa. Waliin dubbachuu dandeenyaa? akkawunti account":"Gargaarsa Herregakoon wal qabatu\n\nEeyyee, Ni dandeessa. Akkasumas wiirtuu gargaarsa maamilaa bilbilaa keenya 609 fayyadamuu dandeessu.",
    "Rakkoo mobaayil baankikoo akkamittin gabaasuu dandaa\'a? mobile bank problem rakkoo mobile bank":"Rakkoo Mobaayil Baankii Gabasuu\n\nDameetti ykn karaa wiirtuu gargaarsa maamilaa(609) gabaasuu dandeessu.",
    "Maaltu coopapp kanneen biroo irraa adda taasisa? Coop app addaa taasisa":"Coop App maaltu adda godha?\n\nCoop App baankii dijitaalaa biroo irraa adda, development environment irraa kaasee hanga tajaajila kennamutti. Coop App moojuulota gurguddoo lama qaba isaanis Retail Banking fi Business Banking dha. Hoggansa maamilaa baankii biroo fi Coopbank, Daddabarsa saganteessuu, Daddabarsa Irra Deddeebi, Daddabarsa Heddumminaan(Business banking kan oolu), Damee fi ATM barbaaduu akkasumas tajaajila isaan kennan fi fageenyaan calaluu, Herrega dursee ilaaluu(Filannoo maamillaan) fi kkf qaba.",
    "Tarkaanfiiwwan nageenyaa akkamii hojiirra olcha? 2FA hojii irra ni olchaa?":"Nageenyaan walqabate\n\nYeroo seentan hunda OTP fayyadamuun nama jette ta\'uu keessan ilaalla. Yeroo Login gootan OTP isiniif erga. OTP kanammoo ofuma isaatiin galfata. Waa\'ee nageenyummaa Coop App caalaatti yoo barbaaddan `Nageenya Coop App` jechuun barreessaa.",
    "Daangaan daddabarsaa meeqa? transfer limit":"Daangaa Daddabarsa\n\nBaankichi wantoota adda addaa kanneen akka dambiiwwan faayinaansii, fedhii maamiltootaa, haala keessoo fi jijjiirama hojii tilmaama keessa galchuun daangaa daldalaa guyyaa guyyaa fi waliigalaa kaa\'uu ni danda\'a",
    "Feature akkami qaba? service provided":"Waantoota inni of keessatti ammatu\n\nRetail Banking\n-Transfer(Own account transfer, transfer to other person, Wallet transfer, both Coopbank and other bank beneficiary management, schedule transfer, repeat transfer, one-time transfer and etc.)\n-Account(You can access your all Coopbank account, account detail, account filter, transaction activities and search, transaction detail, dispute management and etc.)\n-Personalization(You can use 2 local language and English, account balance preview, reset credential, branch and ATM locator)\n-Bill Payment(one-time-bill payment and bill management)\n\nBusiness Banking(All retail banking feature and feature listed below)\n-User management\n-Approval Matrix\n-Bulk Transfer\n-Approval, Request and etc.",
    "Daddabarsa dogoggorameef akkamittan komii dhiyessa Komii? Komii dispute":"Komii Daddabarsaa\n\nBal\'ina daddabarsaa banaa. Komii tuqaa. Sababa komii sanaa filadhaa. Ibsa galchaa komii sana bareessa itti fufi kan jettu tuqa.",
    "Haftee herrega liqiikoo jiru ilaaluu nan danda\'aa? Liqii":"Haftee Liqii ilaaluu\n\nEeyyee, Dasboard irraa herrega liqii keessan filadhaatii mallattoo kan golee mirgaa gubbaatti argamu cuqaasaa.",
    "Tajaajila keessan irratti yaada akkamittan kennuu danda\'a? Yaada kennuu feedback comment":"Yaada Kennuu\n\nYaada keessan karaa Coop App kennuu dandeessu. Qabduu menu golee bitaa gubbaa argamu cuqaasuun; Erga kan jedhu filadhaati mallattoo + tuqa. Naannoo yaada kee irratti kennuu barbaaddan filachuun yaada keessan barreessa ykn faayilii walitti qabaa ergaa.",
    "Tajaajila Retail fi Bizines baankiingii retail and business banking garaagarummaa retail fi bizinesii":"Retail vs. Business Banking\n\nBizinas Baankiing\nBizinas Baankiin maamiltoonni daldalaa faayinaansii isaanii waliin karaa hedduudhaan haala salphaafi nageenyumman isaa eegameen akka walqunnaman kan dandeessisu yoo ta\'u, kunis daldaltoonni adeemsa bulchiinsa faayinaansii isaanii akka salphisan fi herrega isanii irratti olaantummaa hojii akka argatan gargaara.\nRetail Banking\nTeeknooloojiiwwan haaraa fayyadamuun maamiltootaaf muuxannoo faayinaansii dhuunfaa, wal-xaxaa ta\'e bakka tuqaalee dijitaalaa adda addaa irratti uuma. Tajaajila kanneen akka mosaajii bilbilaa fi marsariitiin maamiltootaaf mijatu, odeeffannoo argachuu, fi tajaajila daldalaa yeroo kamiyyuu, bakka kamiyyuu tajaajilu dhiyeessa.",
    "Garaagarummaan Coopay-ebirr fi Coop App maalii? Coopayebirr ebirr":"Garaagarummaa Coopay-ebirr fi Coop App\n\nCoop App waltajjii Omnichannel yoo ta\'u Coopay-ebirr ammoo cross-channel dha. Coop App keessatti maamiltoonni Conventional fi IFB chaanaalii adda addaa kan fayyadaman yoo ta\'u qoqqoodinsi kun Coopay-Ebirr keessatti hin argamu. Coop App fayyadamuun herrega Liqii keessan dabalatee herrega keessan hunda argachuu dandeessu, Coopay-ebirr irratti herrega tokko qofa argachuu dandeessu.",
    "Coop App waltajjii baankii Dhala irraa bilisa ta\'e qabaa? Coop App Alhuda IFB":"Coop App Alhuda(IFB)\n\nEeyyee, Coop App Alhuda mosajjii adda ta\'e kan abbootii herrega tajaajila baankii dhala bilisaa keenyaaf qophaa\'edha.",
    "Tajaajila dijitaala bizinesiif waantoota barbaachisan Business banking criteria":"Business Banking Eligibility\n\nBusiness Registration Documents:\n-Certificate of Incorporation (for corporations)\n-Business Registration Certificate (for sole proprietors/partnerships)\n-Memorandum and Articles of Association (for companies or associations)\nLetter from business entity:\n-If the business entity possesses the authority to manage its signatories or users, the letter from the business entity should include only the necessary information for the General Manager (Administrator).\n-If signatory or user management is overseen by a Coopbank branch, the business entity letter must incorporate the required information for all signatories.\nValid and renewed business license.\nValid and renewed signatory\'s identification documents.\nBoard Resolution or general assembly minute\nThe official application form provided by the bank, fully completed, signed and stamped.",
    "Osoo keessaa hin seeniin haftee ilaaluu account preview":"Account Preivew\n\nDurargii Herregaa amala osoo hin keessa hin seenin haftee keessan arguuf gargaarudha. Filannoon kun durtiidha(default) cufaadha. Yoo filannoo kana yaalu barbaaddan Qindaa\'ina keessa seenuun banu dandeessu.",
    "Akkataa galmee bizinas bankii bizines banki galmaa\'uu business banking regsitration":"Galmee Tajaajila Bankii Bizinasii\n\nTajaajila kanaaf galmaa'uuf damee isinitti dhihoo jiru daawwadhaa.",
    "Network Interneetii Coop app Kun network 3G 4G 5G dhaan ni dalagaa":"Neetworkiin Walqabatee\n\nCoop App 3G, 4G ykn 5G irratti haala gaarii ta'een nii hojjeta.",
    "Akkaataa fayyadama how to use usage Akkamitti fayyadamnaa ":"Tajaajila kannatti fayyadamuuf\n\nJalqaba bakka jirtan kamittiyyuu carraaqqii tokko malee herrega keessan fayyadamuun galmaa'aa. Erga seentanii booda, herrega keessan hunda bakka mijataa tokkotti argachuu dandeessu, kunis daldala walxaxaa fi rakkina irraa bilisa ta'e akka itti gammaddan isin dandeessisa.",
    "your device is not compatible with this version device compatability Device bilbilakoorratti hin hojjetu":"Filannoo Bilbilaa fi Coop App\n\nCoop App Android 9.0 ol irratti hojjeta",
    "Haala Coop App Coop App status":"App Store ykn Play Store irraa Coop App keessan update godhaa. Yoo rakkoon keessan furmaata hin arganne 609 irratti bilbilaa.",
    "Lakkofsa herregaakoo naa ergaa lakk. herregaa na ergaa akkunti na ergaa":"Maaloo damee isinitti dhiyoo jiru quunnamaa.",
    "Maaliif hojjechuu dide? hin hojjetu banuu dide dalagaa hin jiru hin dalagu Coop app Amma hojjechaa hin jiru":"Maaloo 609 irratti bilbiluun wiirtuu gargaarsa maamilaa quunnamaa",
    "how can i activate my account how to activate Coop App coop app activation Coop app active naa godhaa active gochuu":"Coop App Active gochuu\n\n Coop App activate gochuuf jalqaba galmaa\'aa, Activation ID fi Activation Code isiniif ergamu sana itti guutuun maqaa-fayyadamaa(username) fi jecha-darbii(Password) haaraa guuttadhaa.",
    "Webin naa hojjechuu dide web is not working for me web access":"Fayyadama Marsaritiif(Web Access)\n\n Tajaajila gama marsaritiin argachuuf damee isinitti dhiyoo jiru quunnamaa",
    "Account number hunda fidaan jiru herregakoo hunda fidaan jiru akkonti hafetu jira":"Lakk. Herregaa hunda naa fidaan jiru\n\n Herrega kee Dashboard irratti yoo hin mul\'anne maaloo damee sitti dhiyoo jiru daawwachuun herrega kee tajaajilicha irratti dabali."

}

qa_pairs_am = {
    "በCoop App አገልግሎት ላይ እንዴት ይመዝገቡ? በኩፕ አፕ አገልግሎት ላይ እንዴት ይመዝገቡ? ምዝገባ Coop app ይመዝገቡ registration how to register እንዴት መመዝገብ ይቻላል?":"Coop መተግበሪያ ምዝገባ\n\n1. መጀመሪያ ለመመዝገብ የኮፕ ባንክ አካውንት ሊኖርዎ ይገባል።\n2. መተግበሪያውን ከፕሌይ ስቶር ወይም አፕ ስቶር ይጫኑ።\n3. መተግበሪያውን ይክፈቱ።\n4. መዝግብ/አስጀምር የሚለዉን ይምረ።\n5. የግል ባንኪንግ ይምረጡ።\n6. አሁን መመዝገብ የሚለውን ይምረጡ።\n7. የባንክ ሂሳብ እና Captcha ያስገቡ።\n8. አሁን \'አካውንትዎን ያስጀምሩ\' ምረጥ።\n9. በSMS የተላከውን Activation ID እና Activation Code ያስገቡ።\n10. የተጠቃሚ ስም (ቢያንስ 8 ቁምፊዎች) ያስገቡ እና \'Check availability\' የሚለውን ይምረጡ።\n11. የይለፍ ቃል ያስገቡ (ቢያንስ 8 የቁጥርና ፊደላት ቅልቅል መሆን አለበት)።",
    "ዲጂታል ባንክ ተቆልፏል digital bank locked":"ዲጂታል ባንክ ተቆልፏል።\n\nየተሳሳተ የይለፍ ቃል ከ 5 ጊዜ በላይ ከሞከሩ ለ 3 ደቂቃዎች ዲጂታል ባንክዎ ይቆለፋል. ከ 3 ደቂቃዎች በኋላ የይለፍ ቃልዎን ይቀይሩ እና ይግቡ።",
    "የተረሳ የይለፍ ቃል እንዴት መቀየር ይቻላል? የተረሳ password forgotten password reset password ርሴት ፓሥዎርድ ":"የተረሳ የይለፍ ቃል\n\n1. በመግቢያ ገጹ ላይ \'መግባት አልቻሉም?\' የሚለውን ይጫኑ\n2. የግል ባንኪንግ ይምረጡ\n3. በመጀመሪያው መስክ የባንክ ሂሳብ ቁጥርዎን ያስገቡ እና በሁለተኛው መስክ ላይ Captcha ያስገቡ እና የቀጥሉ የሚለዉን ይጫኑ \n4. የተጠቃሚ ስምህን ታገኛለህ እና \'የይለፍ ቃልህን ዳግም አስጀምር\' የሚለውን ተጫን\n5. በSMS ወይም በemail OTP ይላካል እና በራሱም ያስገባል\n6. አዲሱን የይለፍ ቃልዎን ለማስገባት መስኩን ያገኛሉ ከዚያም የይለፍ ቃልዎን በሁለተኛው መስክ ላይ እንደገና ያስገቡ እና ቀጥልን ይጫኑ",
    "የይለፍ ቃሌ ጊዜው አልፎበታል። እንዴት ማስተካከል ይቻላል? expired password":"ጊዜው ያለፈበት የይለፍ ቃል\n\n1. በመግቢያ ገጹ ላይ \'መግባት አልቻሉም?\' የሚለውን ይጫኑ\n2. የግል ባንኪንግ ይምረጡ\n3. በመጀመሪያው መስክ የባንክ ሂሳብ ቁጥርዎን ያስገቡ እና በሁለተኛው መስክ ላይ Captcha ያስገቡ ከዚያ ይቀጥሉ ይጫኑ \n4. የተጠቃሚ ስምህን ታገኛለህ ከዚያም \'የይለፍ ቃልህን ዳግም አስጀምር\' የሚለውን ተጫን\n5. በSMS ወይም በemail OTP ይልካል ከዚያ በራሱ ይቀበላል\n6. አዲሱን የይለፍ ቃልዎን ለማስገባት መስኩን ያገኛሉ እና የይለፍ ቃልዎን በሁለተኛው መስክ ላይ እንደገና ያስገቡ ከዚያም ቀጥልን ይጫኑ",
    "ወደ ሌላ ባንክ ገንዘብ አስተላልፌያለሁ፣ ግን እስካሁን አልደረሰኝም። የዝውውር ጉዳይ transfer issue":"ሌላ የባንክ ማስተላለፍ ጉዳይ\n\nበአጭር ጊዜ ውስጥ ወደ ሂሳብዎ ተመላሽ ይደረጋል። ገንዘቡ እስኪመለስ ድረስ፣ እባክዎን ይታገሱ!",
    "ለCoop App አገልግሎት ምን የመግባት አማራጮች አሉ? ለኩፕ አፕ አገልግሎት ምን የመግባት አማራጮች አሉ? sign-in option sign in option signin":"ኩፕ አፕ መግቢያ አማራጭ\n\n1. የተጠቃሚ ስም እና የይለፍ ቃል\n2. ፒን(PIN)\n3. ባዮሜትሪክስ (ለምሳሌ የጣት አሻራ)",
    "የእኔ ዲጂታል ባንኪንግ ተሰናክሏል። እንደገና እንዴት ማግኘት እችላለሁ? disabled digital bank ዲሰብልድ ኩፕ አፕ":"የተከለከለ ዲጂታል ባንክ\n\nመታወቂያዎን በእጅዎ ይዘው በአቅራቢያዎ ያለውን ቅርንጫፍ ይጎብኙ። ዲጂታል ባንኪንግን እንደገና ለመጀመር የኩፕ አፕ አገልግሎት አስተዳደር ቅጽን ይሞላሉ።",
    "በምዝገባ ወቅት የተጠቃሚ ስም ከስገባን በኋላ የይለፍ ቃል አይወስድም። የይለፍ ቃል መስኩ በምዝገባው ላይ እየሰራ አይደለም password field is not working የይለፍ ቃል መስክ በምዝገባ ላይ አይሰራም ፓሥዎርድ መስክ አይሰራም  ":"የይለፍ ቃል አይወስድም።\n\nየተጠቃሚ ስምዎን ካስገቡ በኋላ በተጠቃሚ ስም መስክ ስር \'Check Availability\' የሚለውን ይጫኑ። \'የተጠቃሚ ስም አለ\' ካሳየ አሁን የይለፍ ቃልዎን ማስገባት ይችላሉ። \'የተጠቃሚ ስም የለም\' ከተባለ ያስገቡት የተጠቃሚ ስም አስቀድሞ በሌላ ተጠቃሚ ተወስዷልና ሌላ ይጠቀሙ።",
    "ራሴን ከማጭበርበር እንዴት እጠብቃለሁ? ማጭበርበር ሌቦች የማጭበርበር ጥበቃ fraud protection frauders":"ከማጭበርበር ይከላከሉ\n\n1. ሲም ካርድዎን በፒን(PIN) ኮድ ይቆልፉ።\n2. በእርስዎ የስክሪን መቆለፊያ ላይ \'PATTERN\'ን ከመጠቀም ይልቅ ፒን(PIN) ወይም የይለፍ ቃል(Password) ለመጠቀም ይሞክሩ።\n3. በሕዝብ ቦታዎች ላይ በጥንቃቄ ይጠቀሙ።\n4. ሲጨርሱ ሁል ጊዜ ከሞባይል ባንኪንግ መተግበሪያዎ ይውጡ።\n5. የመለያዎን እንቅስቃሴ በመደበኛነት ይቆጣጠሩ እንዲሁም ማንኛውንም አጠራጣሪ ግብይት ወዲያውኑ ለባንክ ያሳውቁ።\n6. የይለፍ ቃልዎን በመደበኛነት ይለውጡ።",
    "Coop App ደህንነት ኩፕ አፕ ደህንነት Security":"ኩፕ አፕ ደህንነት\n\nኩፕ አፕ በላቁ ምስጠራ እና ባለ ብዙ ሽፋን ጥበቃን ጨምሮ በዘመናዊ ቴክኖሎጂ የተጠበቀ ነው፣ ሁልጊዜ ደህንነቱ እንደተጠበቀ ይቆያል።",
    "Coop App ምንድን ነው? ኩፕ አፕ ምንድን ነው? ኩፕ አፕ what is coop app":"ኩፕ አፕ ምንድን ነው?\n\nኩፕ አፕ እንከን የለሽ እና የተቀናጀ የባንክ ልምዶችን በበርካታ ቻናሎች ለማቅረብ የተነደፈ ሁሉን አቀፍ ዲጂታል የባንክ መተግበርያ ነው። በሞባይል መሳሪያዎችም ሆነ ድህረገፅ፣ ኩፕ አፕ ደንበኞቻቸው ገንዘባቸውን ያለምንም ልፋት ከየትኛውም ቦታ፣ በማንኛውም ጊዜ ማስተዳደር እንዲችሉ ያደርጋል።",
    "ኩፕ አፕ ለምን? Coop App ለምን? የCoop App አስፈላጊነት የኩፕ አፕ አስፈላጊነት why coop app why coopapp? ":"የኩፕ አፕ አስፈላጊነት\n\n1. ቅልጥፍና\n2. ሁሉን ያማከለ\n3. ወጥነት\n4. ደህንነቱ የተጠበቀ\n5. ተደራሽነት\n6. ፋይናንስ አገልግሎቶችን ይሰጣል",
    "ቢል መክፈል እችላለሁ? ቢል ክፍያ bill payment":"ቢል መክፈል እችላለሁ?\n\nየኢትዮጵያ አየር መንገድ፣ Canal+፣ DSTV እና የመሳሰሉትን ቢል መክፈል ይችላሉ።",
    "በባንክ ሂሳብ ላይ እገዛ እፈልጋለሁ። ተወካይ ማናገር እችላለሁ? account problem":"በባንክ ሂሳብ ላይ እገዛ\n\nአዎ፣ ትችላለህ። ለበለጠ መረጃ የእኛን የጥሪ ማእከል ማለትም 609 መጠቀም ይችላሉ።",
    "በእኔ ሞባይል ባንኪንግ ላይ ችግር እንዳለ እንዴት ሪፖርት አደርጋለሁ? mobile bank ችግር mobile banking problem mobile bank problem":"ሞባይል ባንኪንግ ችግር ሪፖርት ማድረግ\n\nበቅርንጫፍ ወይም በጥሪ ማእከል ሪፖርት ማድረግ ይችላሉ.",
    "Coopappን ከሌሎች የሚለየው ምንድን ነው? ኩፕ አፕ ከሌሎች የሚለየው ምንድን?":"ኩፕ አፕ ከሌሎች የሚለየው ምንድን?\n\nኩፕ አፕ ከሌሎች ዲጂታል ባንኪንግ ከ development environment በዚህ አፕ ከሚሰጠው አገልግሎት ይለያል። ኩፕ አፕ ሁለት ዋና ዋና ሞጁሎች አሉት እነሱም የግል ባንኪንግ እና ቢዝነስ ባንክ ናቸው። የራሱ የሌላ ባንክ እና የኩፕባንክ ተጠቃሚ አስተዳደር፣ የመርሐግብር ማስተላለፍ፣ ተደጋጋሚ ማስተላለፍ፣ የጅምላ ማስተላለፍ(ቢዝነስ ባንክ ባህሪ)፣ ቅርንጫፍ እና ኤቲኤም አመልካች በሚሰጡት አገልግሎት ማጣሪያ እና ርቀት፣ የሂሳብ ቅድመ እይታ(የተጠቃሚ ምርጫ) እና ወዘተ አለው።",
    "ምን ዓይነት የደህንነት እርምጃዎች አሉ? ባለብዙ ደረጃ ማረጋገጫን ያቀርባል?":"የደህንነት እርምጃዎች\n\nበገቡ ቁጥር የ OTP ዘዴን ተጠቅመው እርስዎ መሆንዎን እናረጋግጣለን። ስትገቡ OTP ይልክልዎታል እና መተግበሪያው በራሱ OTP ያስገባል። ስለ ኩፕ አፕ ደህንነት ተጨማሪ ከፈለጉ `ኩፕ አፕ ደህንነት` ብለው ላኩልን።",
    "የዝውውር ገደቦች ምን ያህል ናቸው? transfer limit":"የዝውውር ገደቦች\n\nእንደ የፋይናንስ ደንቦች, የደንበኞች መስፈርቶች, የውስጥ ሁኔታዎች እና የአሠራር ተለዋዋጭነት የመሳሰሉ የተለያዩ ሁኔታዎችን ከግምት ውስጥ በማስገባት ባንኩ ሁለቱንም ዕለታዊ እና አጠቃላይ የግብይት ገደቦችን ማዘጋጀት ይችላል።",
    "የሞባይል ባንኪንግ ምን አገልግሎት ይሰጣል? features service":"የሚሰጠው አገልግሎት\n\nRetail Banking\n-ማስተላለፍ(የግል አካዉንት ማስተላለፍ, ወደ ሌላ ሰው አካዉንት ማስተላለፍ, የዋሌት ማስተላለፍ, የባንካችንም ሆነ የሌላ ባንክ ተጠቃሚዎች አስተዳደር, ግብይይቶችን ማቀድ, ግብይይቶችን መድገም, የአንድ ጊዜ ማስተላለፍና ሌሎችም.)\n-አካዉንት(በባንካችን ያለዎትን ሁሉንም አካዉንቶች በ አንድ መተግበርያ መጠቀም ያስችላል, የአካዉንት ዝርዝር, የአካዉንት ማጣራት, የግብይይት እንቅስቃሴና ፍለጋ, የግብይይት ዝርዝር, ቅሬታ ማንሳትና የመሳሰሉትን ይጨምራል)\n-ግላዊ ማጣሪያዎች(በሶስት ቋንቋዎች ያገኛሉ, የአካዉንት ቀሪ ሂሳብ ቅድመ እይታ, የይለፍ ቃል ዳግም ማስጀመር, ቅርንጫፍና ኤቲኤም መፈለግያ)\n-የቢል ክፍያ(የአንድ ጊዜ ቢል መክፈል እንዲሁም ቢሎችን ማስተዳደር)\n\nየቢዝነስ ባንኪንግ(ሁሉንም የግል ባንኪንግ አገልግሎቶች ጨምሮ ከዚህ በታች የተዘረዘሩትን አገልግሎቶች፡)\n-የተጠቃሚዎች አስተዳደር\n-አፕሩቫል ማትሪክስ\n-የጅምላ ክፍያ\n-ማጽድቆች, ጥያቄዎችና ሌሎችም",
    "ለተሳሳተ ግብይት ቅሬታ እንዴት ማቅረብ እችላለሁ? dispute":"ተሳሳተ ግብይት ቅሬታ ማቅረብ\n\nየግብይቱን ዝርዝር ይክፈቱ። የቅሬታ ግብይትን ይጫኑ። የቅሬታውን ምክንያት ይምረጡ። መግለጫውን ያስገቡ እና ቀጥልን ይጫኑ።",
    "የብድር ቀሪ ሒሳቤን ማረጋገጥ እችላለሁ? loan ብድር loan available balance":"ብድር ቀሪ ሒሳቤን ማረጋገጥ\n\nአዎ፣ ከዳሽቦርዱ የብድር ሂሳብዎን ይምረጡ እና በስክሪኑ ላይኛው ቀኝ ጥግ ላይ ያለውን ይጫኑ።",
    "በአገልግሎቶችዎ ላይ እንዴት አስተያየት መስጠት እችላለሁ? አስተያየት feedback comment":"አስተያየት መስጠት\n\nአስተያየትዎን በኩፕ አፕ በኩል መስጠት ይችላሉ። ከላይ በግራ በኩል የሚገኘውን \'Menu\' ቁልፍ ይጫኑ መልዕክቶችን ይጫኑ፣ + ምልክትን ይጫኑ፣ የግብረመልስዎን አካባቢ ይምረጡ፣ ግብረ መልስዎን ያስገቡ ወይም ፋይል ያያይዙ እና ይላኩት።",
    "ርቴል ባንኪንግ እና ቢዝነስ ባንኪንግ Retail vs. Business Banking difference":"ርቴል ባንኪንግ እና ቢዝነስ ባንኪንግ\n\nቢዝነስ ባንኪንግ\nየቢዝነስ ባንኪንግ የቢዝነስ ደንበኞቻቸው ገንዘቦቻቸውን ያለምንም እንከን በበርካታ ቻናሎች እንዲገናኙ ያስችላቸዋል፣ ይህም ንግዶች የፋይናንሺያል አስተዳደር ሂደቶቻቸውን እንዲያቃልሉ እና በመጨረሻም የተግባር የላቀ ውጤት እንዲያመጡ ያግዛል።\nርቴል ባንኪንግ\nበተለያዩ ዲጂታል የመዳሰሻ ነጥቦች ላይ ለደንበኞች ግላዊ እና እንከን የለሽ ተሞክሮዎችን ለመፍጠር አዳዲስ ቴክኖሎጂዎችን ይጠቀማል። የደንበኞችን ምቾት፣ የመረጃ ተደራሽነት እና የግብይት አገልግሎቶችን በማንኛውም ጊዜ እና ቦታ የሞባይል መተግበሪያ ወይም ድህረገፅ አገልግሎቶችን ያቀርባል።",
    "የ Coopay-ebirr እና ኩፕ አፕ ልዩነት ምንድነው? Coop App vs. Ebirr coopay-ebirr":"Coopay-ebirr እና Coop App ልዩነት\n\nኮፕ አፕ የኦምኒቻናል ፕላትፎርም ሲሆን ኩፓይ ኤቢር ደግሞ ክሮስ-ቻናል ነው። በCoop App Conventional እና IFB ደንበኞች የተለየ ቻናል ይጠቀማሉ እና ይህ ክፍል በCoopay-Ebirr ውስጥ አይገኝም። ኮፕ አፕ የኦምኒቻናል መድረክ ሲሆን ኩፓይ ኤቢር ደግሞ ክሮስ-ቻናል ነው። በCoop App Conventional እና IFB ደንበኞች የተለየ ቻናል ይጠቀማሉ እና ይህ ክፍል በCoopay-Ebirr ውስጥ አይገኝም። ኩፕ አፕ በመጠቀም የብድር ሂሳብ ጨምሮ ሁሉንም ሂሳቦችዎን መድረስ ይችላሉ ፣ በ Coopay-ebirr ላይ አንድ ሂሳብ ብቻ መድረስ ይችላሉ።",
    "ኩፕ አፕ ከወለድ ነፃ የባንክ አፕ አለው? Coop App Alhuda IFB":"Coop App Alhuda(IFB)\n\nአዎ፣ Coop App Alhuda ከወለድ ነፃ የባንክ አካውንት ባለቤቶች የቀረበ የተለየ መተግበሪያ ነው።",
    "ለ ቢዝነስ ደንበኛ ብቁ የሆነ ሰነድ Eligible document for business customer":"ቢዝነስ ደንበኛ ብቁ የሆነ ሰነድ\n\nBusiness Registration Documents:\n-የንግድ ምዝገባ(ለቢዝነስ ባንኪንግ)\n-የንግድ ምዝገባ\n-መመስረቻ ጽሁፍ\nከአመልካቹ ድርጅት መጠየቅያ ደብዳቤ:\n-ድርጅቱ የሚንቀሳቀሰዉ በአንድ ሰዉ ብቻ ከሆነ ደብዳቤዉ ላይ መካተት ያለበት የማናጀሩ መጠየቅያ ይሆናል።\n-ሁሉንም ፈራሚዎች የሚቆጣጠረዉ ባንኩ ከሆነ ደግሞ የሁሉም ፈራሚዎች መረጃ በ ደብዳቤዉ ላይ መካተት አለበት።\nየታደሰ የንግድ ፈቃድ\nየታደሰ የፈራሚዎች መታወቅያ\nጠቅላላ ጉባኤ ዉሳኔ ካለ ይካተታል\nበባንኩ እና በድርጅቱ የሚፈረም መሃተም የተደረገበት ሰነድ መቅረብ ይኖርበታል።",
    "ሂሳብ ቅድመ እይታ ያለመግባት ያለዎትን ቀሪ ሒሳብ ለማየት Account preview":"Account Preview\n\nየሂሳብ ቅድመ እይታ ወደ አካዉንትዎ መግባት ሳያስፈልግዎ ያለዎትን ቀሪ ሒሳብ ለማየት የሚያግዝ አገልግሎት ነው። ይህ አማራጭ በነባሪ ተዘግቷል። ይህን ባህሪ መሞከር ከፈለጉ ከመቼቶች(setting) ውስጥ መክፈት ይችላሉ።",
    "Business Banking Registration የቢዝነስ ባንኪንግ ምዝገባ":"የቢዝነስ ባንኪንግ ምዝገባ\n\nለዚህ አገልግሎት ለመመዝገብ እባክዎ በአቅራቢያዎ የሚገኘውን ቅርንጫፍ ይጎብኙ።",
    "Network  ነትዎርክ":"ከአውታረ መረብ ( ነትዎርክ)ጋር የተያያዘ\n\nCoop መተግበሪያ በ3ጂ፣ 4ጂ ወይም 5ጂ ላይ ይሰራል።",
    "Coop መተግበሪያ አጠቃቀም Coop  App  አጠቃቀም":"Coop App አጠቃቀም\n\nመጀመሪያ የትም ይሁኑ የትም የሂሳብ ቁጥርዎን በመጠቀም የተጠቃሚ መለያዎን ያስመዝግቡ። ከገቡ በኋላ፣ ሁሉንም የሂሳብ ዝርዝሮችዎን በአንድ ምቹ ቦታ ያገኛሉ፣ ይህም ያለምንም እንከን የለሽ እና ከችግር ነፃ በሆነ ግብይት እንዲደሰቱ ያስችልዎታል።",
    "your device is not compatible with this version device compatability Device የሞባይል ምርጫ ሞባይል ምርጫ":"የሞባይል ምርጫ\n\nCoop መተግበሪያ በአንድሮይድ 9.0 እና ከዚያ በላይ ላይ ይሰራል",
    "Coop App ሁኔታ Coop App is not working for me Coop App Status":"Coop App ሁኔታ\n\nእባክዎ የእርስዎን Coop App መተግበሪያ ከApp Store ወይም Play Store ያዘምኑ። ችግሩ ካልተፈታ በ609 ይደውሉልን።",
    "አካውንት ቁጥሬን ላክልኝ my account number":"እባክዎን በአቅራቢያ የሚገኘውን ቅርንጫፍ ይጎብኙ",
    "Coop App እየሰራ አይደለም አይሰራም አይሠራም not working":"እባክዎ የጥሪ ማእከልን 609 ያግኙ",
    "how can i activate my account how to activate Coop App coop app activation እንዴት Activate ማድረግ እችላለሁ? Coop Appን እንዴት ማንቃት ይቻላል?" :"COOP APPን ለመጀመር መጀመሪያ ይመዝገቡ እና ሲስተም Activation ID እና Activation ኮድ ይልክልዎታል። በምትኩ Activation ID  እና Activation ኮድ አስገባ። ለመፍጠር በተሰጡት መስኮች ውስጥ የተጠቃሚ ስምህን (username) እና የይለፍ ቃልህን (password) አስገባ።",
    "ድህረገፅ አይሰራም web access web is not working for me":"ድህረገፅ መዳረሻ\n\nየድህረገፅ መዳረሻ ለማግኘት ከፈለጉ እባክዎን በአቅራቢያዎ የሚገኘውን ቅርንጫፍ ይጎብኙ።",
    "የሂሳብ ቁጥሬን አጣሁ የሂሳብ ቁጥሬን እያሳየ አይደለም ሁሉንም የሂሳብ ቁጥሬን እያሳየ አይደለም":"የጠፋ የሂሳብ ቁጥር\n\nየሂሳብ ቁጥርዎ በዳሽቦርዱ ላይ ካልታየ እባክዎ የሂሳብ ቁጥርዎን ወደ አገልግሎት ለመጨመር በአቅራቢያዎ የሚገኘውን ቅርንጫፍ ይጎብኙ።"

}

def find_best_match(context, update, question, qa_pairs):
    log_interaction(update)
    global lang_faq
    global admin_user

    best_match, score = process.extractOne(question, qa_pairs.keys(), scorer=fuzz.token_set_ratio)
    if score >= 40:
        return qa_pairs[best_match]
    else:
        message_text = "Question : " + question + " is asked."
        context.bot.send_message(chat_id=admin_user, text=message_text)
        if lang_faq == 'en':
            return "I'm sorry, Wait for me."
        elif lang_faq == 'oro':
            return "Dhiifama! Xiqqoo na eegi."
        else:
            return "ይቅርታ ትንሽ ጠብቀኝ"




def start(update: Update, context: CallbackContext) -> None:
    log_interaction(update)
    global lang_id
    global user_id_global
    global username_global
    if lang_id == 0:
        welcome_image_url = 'https://ibb.co/0KCgK9g'
    else:
        welcome_image_url = 'https://i.ibb.co/m5YR1Gs/lang.png'
        lang_id = 0

    user = update.message.from_user
    # text = update.message.text
    first_names = user.first_name
    last_names = user.last_name

    if first_names == 'None' or first_names == None:
        first_name = user.username
    if last_names == 'None' or last_names == None:
        last_names = ''
    user_id_global = update.message.chat_id

    if user_id_global != None:
        xusername =read_user_data(str(user_id_global))
        xusername_splited = xusername.split("+")
        xlang = xusername_splited[1]

    if xlang != None:
        lang_perf = xlang
    username_global = update.message.chat.username or update.message.from_user.full_name


    # logger.info(f"Message from {user.username}: {text}")
    # logger.info(f"First Name: {first_names} {last_names}")
    welcome_text = 'Akkam jirta *'+first_names+' '+last_names+'*! Ani bootii gargaarsaa Coop App* keessaniiti.\n\nHello *'+first_names+' '+last_names+'*! I am your Coop App* assistance bot.\n\nሰላም *' + first_names + ' ' + last_names + '* እኔ የእርስዎ ኩፕ አፕ እገዛ ቦት ነኝ።'
    update.message.reply_photo(photo=welcome_image_url, caption=welcome_text, parse_mode=ParseMode.MARKDOWN)
    keyboard = [[InlineKeyboardButton("Afaan Oromoo", callback_data='oro'), InlineKeyboardButton("English", callback_data='en'), InlineKeyboardButton("አማርኛ", callback_data='am')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('🌐 Maaloo Qooqa filadhaa: 🌐 \n\n🌐 Please select your language: 🌐 \n\n 🌐 እባክዎ ቋንቋዎን ይምረጡ፡- 🌐', reply_markup=reply_markup)

def download_app(update: Update, context: CallbackContext) -> None:
    log_interaction(update)
    global lang_perf, user_id_global
    if lang_perf == None or lang_perf == '':
        if user_id_global == None or user_id_global =='':
            user_id_global = update.message.chat_id
        xusername =read_user_data(str(user_id_global))
        xusername_splited = xusername.split("+")
        lang_perf = xusername_splited[1]

    app_image_url = 'https://ibb.co/0sG0Rvy'
    app_download_text = ''
    android_device_text = ''
    ios_device_text = ''
    if lang_perf == 'en':
        app_download_text = 'You can download Coop App from APP Store or Play Store. Click button below.'
        android_device_text = 'Download Link For Android:'
        ios_device_text = 'Download Link For IOS:'
    elif lang_perf == 'oro':
        app_download_text = 'Mosaajjii \'Coop App\' App Store ykn Play Store irraa buufachuu dandeessu. Cunquu gadii cuqaasaa.'
        android_device_text = 'Hidhaa(Link) bibila \'Android\'f:'
        ios_device_text = 'Hidhaa(Link) bibila \'IOS\'f:'
    else:
        app_download_text = 'ኩፕ አፕን App Store ወይም Play Store ማውረድ ይችላሉ። ከታች ያለውን ተጫን።'
        android_device_text = 'ለአንድሮይድ ዳውንሎድ ሊንክ'
        ios_device_text = 'ለ IOS ዳውንሎድ ሊንክ:'
    update.message.reply_photo(photo=app_image_url, caption=app_download_text, parse_mode=ParseMode.MARKDOWN)
    keyboard = [[InlineKeyboardButton("Coop App", url="https://play.google.com/store/apps/details?id=com.coopbankoromiasc.OLB"), InlineKeyboardButton("Coop App Alhuda", url="https://play.google.com/store/apps/details?id=com.coopbankoromiasc.islamic.OnlineBanking"), ]]
    keyboard_ios = [[InlineKeyboardButton("Coop App", url="https://apps.apple.com/ao/app/coop-app/id6467006218"), InlineKeyboardButton("Coop App Alhuda", url="https://apps.apple.com/ao/app/coop-app/id6467006218"), ]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    reply_markup_ios = InlineKeyboardMarkup(keyboard_ios)
    # update.message.bot.send_message(chat_id=update.message.chat_id, reply_markup=reply_markup)
    update.message.bot.send_message(chat_id=update.message.chat_id, text=android_device_text, reply_markup=reply_markup)
    update.message.bot.send_message(chat_id=update.message.chat_id, text=ios_device_text, reply_markup=reply_markup_ios)
    # update.message.reply(reply_markup=reply_markup)


def language_selection(update: Update, context: CallbackContext) -> None:
    # log_interaction(update)
    query = update.callback_query
    global lang_faq, lang_to_save, lang_perf
    global user_id_global, username_global
    if query:
        query.answer()
        # logger.info(f"Callback data: {query.data}")
        user_datas = context.user_data
        user_datas['language'] = query.data
        texted = ''
        if query.data == 'en':
            query.edit_message_text(text="You have selected English. Ask me anything about Coop App.")
            texted = 'Thank you for choosing Coop App!'
            lang_faq = 'en'
            lang_perf = 'en'
        elif query.data == 'oro':
            query.edit_message_text(text="Qooqni filattan Afaan Oromoodha. Waa\'ee \'Coop App\' waan feetan na gaafadhaa.")
            # texted = 'Qooqni filattan Afaan Oromoodha. Filannoo armaan gadii filadhaa ykn waa\'ee \'Coop App\' waan feetan na gaafadhaa.'
            texted = 'Filannoo Keessan Coop App waan godhattaniif galatoomaa!'
            lang_faq = "oro"
            lang_perf = 'oro'
        else:
            query.edit_message_text(text="አማርኛ መርጠዋል። ስለ ኩፕ አፕ ማንኛውንም ነገር ጠይቀኝ")
            texted = 'ኩፕ አፕ ስለመረጡ እናመሰግናለን!'
            lang_faq = 'am'
            lang_perf = 'am'

        user_id = str(user_id_global)
        user_lang = str(username_global)+'+'+lang_faq
        # logger.info(f"username: " + user_lang + " id" + str(user_id))
        # logger.info(f"Language ID: " + str(lang_to_save))
        if lang_to_save == 0:
            if user_id not in user_data:
                # logger.info(f"New users.")
                user_data[user_id] = user_lang
                save_user_data()
        else:
            # logger.info(f"Old users.")
            user_data[user_id] = user_lang
            save_user_data()

        if(query.data == 'en'):
            keyboard = [
                [KeyboardButton("Start 🚀"), KeyboardButton("Language 🌐")],
                [KeyboardButton("Contact Us 📞"), KeyboardButton("FAQ ❓")]
            ]
        elif(query.data == 'oro'):
             keyboard = [
               [KeyboardButton("Jalqabsiisi🚀"), KeyboardButton("Qooqa 🌐")],
               [KeyboardButton("Nu quunnami📞"), KeyboardButton("Gaaffilee ❓")]
            ]
        else:
             keyboard = [
                [KeyboardButton("ጀምር🚀"), KeyboardButton("ቋንቋ🌐")],
                [KeyboardButton("ያግኙን📞"), KeyboardButton("ጥያቄዎች❓")]
            ]

        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        context.bot.send_message(chat_id=query.message.chat_id, text=texted, reply_markup=reply_markup)
    else:
        logger.warning("No callback query received")


def question_list(update: Update, context : CallbackContext, faqs, prefix):
    log_interaction(update)
    global lang_faq, lang_perf, user_id_global
    if lang_perf == None or lang_perf == '':
        if user_id_global == None or user_id_global =='':
            user_id_global = update.message.chat_id
        xusername =read_user_data(str(user_id_global))
        xusername_splited = xusername.split("+")
        lang_perf = xusername_splited[1]
    faq_title = ''
    if lang_perf == "en":
        faq_title = 'Frequently Asked Questions:'
    elif lang_perf == 'oro':
        faq_title = 'Gaaffilee irra deddeebiin gaafataman:'
    else:
        faq_title = 'በተደጋጋሚ የሚጠየቁ ጥያቄዎች:'
    keyboard = []
    for faq_b in faqs:
        button = InlineKeyboardButton(text=faq_b, callback_data=f"{prefix}{faq_b}")
        keyboard.append([button])
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(faq_title, reply_markup=reply_markup)


def faq_button_handler(update: Update, context: CallbackContext) :
    log_interaction(update)
    global lang_perf, user_id_global
    if lang_perf == None or lang_perf == '':
        if user_id_global == None or user_id_global =='':
            user_id_global = update.message.chat_id
        xusername =read_user_data(str(user_id_global))
        xusername_splited = xusername.split("+")
        lang_perf = xusername_splited[1]
    faq_answers = ''
    query = update.callback_query
    query.answer()
    quest = query.data.replace("faquestion_", "")
    if lang_perf == 'en':
        faq_answers = find_best_match(context, update, quest, qa_pairs_en)
    elif lang_perf == 'oro':
        faq_answers = find_best_match(context, update, quest, qa_pairs_oro)
    else:
        faq_answers = find_best_match(context, update, quest, qa_pairs_am)
    query.edit_message_text(text=faq_answers)
    # update.message.reply_text(faq_answers);

def exchange_rate(update: Update, contex: CallbackContext):
    log_interaction(update)
    global lang_perf, user_id_global
    if lang_perf == None or lang_perf == '':
        if user_id_global == None or user_id_global =='':
            user_id_global = update.message.chat_id
        xusername =read_user_data(str(user_id_global))
        xusername_splited = xusername.split("+")
        lang_perf = xusername_splited[1]
    link_title = ''
    if lang_perf == 'oro':
        keyboard = [[InlineKeyboardButton("Marsariitii Daawwadhaa", url="https://coopbankoromia.com.et/daily-exchange-rates/")]]
        link_title = 'Hidhaa gadii cuqaasuun oolmaa sharafaa ilaalaa'
    elif lang_perf == 'en':
        keyboard = [[InlineKeyboardButton("Visit Website", url="https://coopbankoromia.com.et/daily-exchange-rates/")]]
        link_title = 'Click below link to visit exchange rate'
    else:
        keyboard = [[InlineKeyboardButton("ድህረ ገጽን ይጎብኙ", url="https://coopbankoromia.com.et/daily-exchange-rates/")]]
        link_title = 'የምንዛሪ ዋጋን ለመጎብኘት ከታች ያለውን ሊንክ ይጫኑ'

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(link_title, reply_markup=reply_markup)

def handle_start(update: Update, context: CallbackContext) -> None:
    start(update, context)

def handle_language(update: Update, context: CallbackContext) -> None:
    print('Langed handl_lang: '+str(lang_id))
    lang = 'https://i.ibb.co/m5YR1Gs/lang.png'
    lang_label='Maaloo Afaan filadhaa:\n\nPlease select your language:\n\nእባክዎ ቋንቋዎን ይምረጡ፡'
    keyboard = [
        [InlineKeyboardButton("Afaan Oromoo", callback_data=f'oro'), InlineKeyboardButton("አማርኛ", callback_data='am'), InlineKeyboardButton("English", callback_data='en')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_photo(photo=lang, caption=lang_label, reply_markup=reply_markup)

def handle_contact_us(update: Update, context: CallbackContext) -> None:
    # log_interaction(update)
    global lang_perf, user_id_global
    phone_number = 609
    if lang_perf == None or lang_perf == '':
        if user_id_global == None or user_id_global =='':
            user_id_global = update.message.chat_id
        xusername =read_user_data(str(user_id_global))
        xusername_splited = xusername.split("+")
        lang_perf = xusername_splited[1]
    if lang_perf == 'en':
        # support = "♾Contact us♾\n\nFor any Coop App related support kindly use the telephone number listed below.\n☎️ +251 115 589 694\n☎️ +251 115 588 926\n☎️ +251 115 585 943\n\n Also you can contact us through our email address:\n📧 coopapp.support@coopbankoromiasc.com\nTelegram Group:\n✍️  @CoopApp"
        support = "♾Contact us♾\n\nFor any Coop App related support kindly use the telephone number listed below.\n☎️  `609`\n Also you can contact us through our email address:\n📧 coopapp.support@coopbankoromiasc.com\nTelegram Group:\n✍️  @CoopApp"


    elif lang_perf == 'oro':
        support = "♾Nu quunnamaa♾\n\nDeeggarsa Coop App wajjin walqabatu kamiifuu lakkoofsa bilbilaa armaan gadii kana fayyadamaa.\n☎️ `609`\n Akkasumas karaa E-mail keenyaa nu qunnamuu dandeessu:\n📧 coopapp.support@coopbankoromiasc.com\nGaree Teelegiramii:\n✍️  @CoopApp"
        # support = "♾Nu quunnamaa♾\n\nDeeggarsa Coop App wajjin walqabatu kamiifuu lakkoofsa bilbilaa armaan gadii kana fayyadamaa.\n☎️ +251 115 589 694\n☎️ +251 115 588 926\n☎️ +251 115 585 943\n\n Akkasumas karaa E-mail keenyaa nu qunnamuu dandeessu:\n📧 coopapp.support@coopbankoromiasc.com\nGaree Teelegiramii:\n✍️  @CoopApp"
    else:
        support = "♾ያግኙን♾\n\nለማንኛውም ከኩፕ አፕ ጋር ለተያያዘ ድጋፍ ከዚህ በታች የተዘረዘረውን ስልክ ቁጥር በደግነት ይጠቀሙ.\n☎️  `609`\n እንዲሁም በኢሜል አድራሻችን ሊያገኙን ይችላሉ፡-\n📧 coopapp.support@coopbankoromiasc.com\nቴሌግራም ገሩፕ:\n✍️  @CoopApp"
    customer_support = 'https://i.ibb.co/HFMWxmB/Contact-us.png'

    update.message.reply_photo(photo=customer_support, caption=support, parse_mode=ParseMode.MARKDOWN)

def send_message(update: Update, context: CallbackContext):
    log_interaction(update)
    global admin_user
    logger.info(admin_user)
    logger.info(update.message.chat_id)
    if str(update.message.chat_id) != str(admin_user):
        update.message.reply_text("You are not authorized to use this command.")
        message_text = "Unauthorized:  "+ str(update.message.chat_id) + " is trying to use /send option"
        context.bot.send_message(chat_id=admin_user, text=message_text)
        return

    # Check if the admin provided sufficient arguments
    if len(context.args) < 2:
        update.message.reply_text("Usage: /send <user_chat_id> <message>")
        return

    user_chat_id = context.args[0]
    message_text = ' '.join(context.args[1:])

    try:
        message_sent = context.bot.send_message(chat_id=user_chat_id, text=message_text)
        message_ids = message_sent.message_id
        update.message.reply_text(f"Message sent to {user_chat_id}.")
        update.message.reply_text(f"Message ID: {message_ids}")
    except Exception as e:
        update.message.reply_text(f"Failed to send message: {e}")
def delete_message(update: Update, context: CallbackContext):
    log_interaction(update)
    global admin_user
    logger.info(admin_user)
    logger.info(update.message.chat_id)
    if str(update.message.chat_id) != str(admin_user):
        update.message.reply_text("You are not authorized to use this command.")
        message_text = "Unauthorized:  "+ str(update.message.chat_id) + " is trying to use /delete option"
        context.bot.send_message(chat_id=admin_user, text=message_text)
        return

    if len(context.args) < 2:
        update.message.reply_text("Usage: /delete <user_chat_id> <message_id>")
        return
    user_chat_id = context.args[0]
    message_id = ' '.join(context.args[1:])
    try:
        context.bot.delete_message(chat_id=user_chat_id, message_id=message_id)
        update.message.reply_text(f"Message deleted for {user_chat_id} .")
    except Exception as e:
        update.message.reply_text(f"Failed to delete message: {e}")

#let's delete broadcast messages
def delete_broadcast(update: Update, context: CallbackContext):
    log_interaction(update)
    global admin_user
    if str(update.message.chat_id) != str(admin_user):
        update.message.reply_text("You are not authorized to use this command.")
        message_text = "Unauthorized:  "+ str(update.message.chat_id) + " is trying to use /delete option"
        context.bot.send_message(chat_id=admin_user, text=message_text)
        return
    with open(BROADCAST_FILE, 'r') as file:
        data = json.load(file)

    key_left = "Test"
    value_left = "Test"
    new_data = {
        "broadcasted": [
            {
            key_left: value_left
            }
        ]
        }

    deleted_counter = 0
    for entry in data.get("broadcasted", []):
        for key, value in entry.items():
            if key == key_left and value == value_left:
                continue
            try:
                context.bot.delete_message(chat_id=key, message_id=value)
                logger.info(f"Key: " + str(key) + "Value: "  + str(value) + "deleted successfully")
                deleted_counter = deleted_counter + 1
            except Exception as e:
                update.message.reply_text(f"Failed to delete broadcast message: {e}")
    # with open(BROADCAST_FILE, 'w') as file:
    #     json.dump(new_data, file, indent=4)
    deleted_success = "Broadcast Message Deleted for " + str(deleted_counter) + " user successfully!"
    context.bot.send_message(chat_id=admin_user, text=deleted_success)

def broadcast_verification(update: Update, context: CallbackContext):
    log_interaction(update)
    global admin_user
    if str(update.message.chat_id) != str(admin_user):
        update.message.reply_text("You are not authorized to use this command.")
        message_text = "Unauthorized:  "+ str(update.message.chat_id) + " is trying to use /verify option"
        context.bot.send_message(chat_id=admin_user, text=message_text)
        return
    with open(BROADCAST_FILE, 'r') as file:
        data = json.load(file)
    key_left = "Test"
    value_left = "Test"
    new_data = {
        "broadcasted": [
            {
            key_left: value_left
            }
        ]
        }
    with open(BROADCAST_FILE, 'w') as file:
        json.dump(new_data, file, indent=4)
    context.bot.send_message(chat_id=admin_user, text="Broadcast Message verified successfully!")

# Send only Text
def broadcast_message(update: Update, context: CallbackContext):
    log_interaction(update)
    logger.info("text")
    global admin_user
    if str(update.message.chat_id) != str(admin_user):
        update.message.reply_text("You are not authorized to use this command.")
        return

    # Check if the admin provided a message
    if len(context.args) == 0:
        update.message.reply_text("Usage: /broadcast <message>")
        return
    with open(BROADCAST_FILE, 'r') as file:
      data = json.load(file)

    message_text = ' '.join(context.args)
    paragraphs = message_text.split(' / ')


    final_message_text = '\n\n'.join(paragraphs)
    failed_sends = 0

    for user_id in user_data:
        try:
            message_sent = context.bot.send_message(chat_id=user_id, text=final_message_text)
            message_ids = message_sent.message_id
            sent_to_username = message_sent.chat.username if message_sent.chat.username else "No username"
            receiver_id = message_sent.chat.id
            update.message.reply_text(f"Message ID: {message_ids}\nUsername: {sent_to_username}\nUser ID: {receiver_id}")
            # broadcast_data[receiver_id] = message_ids

            for entry in data.get("broadcasted", []):
                entry[receiver_id] = message_ids
            with open(BROADCAST_FILE, 'w') as file:
                json.dump(data, file, indent=4)

            # save_message_data()
        except Exception as e:
            failed_sends += 1
            message_text = "Failed to send message to {user_id}: {e}"
            context.bot.send_message(chat_id=admin_user, text=message_text)


    update.message.reply_text(f"Message sent to all users! Failed to send to {failed_sends} users.\n\n Please check your broadcast message and verify it by sending /verify_broadcast.\n\n If broadcasted message has an error or incorrect please send /delete_broadcast")

def broadcast_message_image(update: Update, context: CallbackContext):
    log_interaction(update)
    logger.info("Image")
    global admin_user


    if str(update.message.chat_id) != str(admin_user):
        update.message.reply_text("You are not authorized to use this command.")
        return


    if len(context.args) < 2:
        update.message.reply_text("Usage: /broadcastimage <message1> <message2> <message3 (optional)> <image_url_or_path>")
        return
    with open(BROADCAST_FILE, 'r') as file:
      data = json.load(file)


    image_path = context.args[-1]


    message_parts = context.args[:-1]
    message_text = ' '.join(message_parts)


    paragraphs = message_text.split(' / ')


    final_message_text = '\n\n'.join(paragraphs)

    logger.info(f"Image url: {image_path}")
    logger.info(f"Message: {final_message_text}")

    failed_sends = 0


    print(f"Broadcasting message:\n{final_message_text}\nWith image: {image_path}")


    for user_id in user_data:
        try:
            message_sent = context.bot.send_photo(chat_id=user_id, photo=image_path, caption=final_message_text)
            message_ids = message_sent.message_id
            sent_to_username = message_sent.chat.username if message_sent.chat.username else "No username"
            receiver_id = message_sent.chat.id
            update.message.reply_text(f"Message ID: {message_ids}\nUsername: {sent_to_username}\nUser ID: {receiver_id}")
            for entry in data.get("broadcasted", []):
                entry[receiver_id] = message_ids
            with open(BROADCAST_FILE, 'w') as file:
                json.dump(data, file, indent=4)
        except Exception as e:
            failed_sends += 1
            print(f"Failed to send message to {user_id}: {e}")
            context.bot.send_message(chat_id=admin_user, text=f"Failed to send message to {user_id}: {e}")

    update.message.reply_text(f"Message sent to all users! Failed to send to {failed_sends} users.")



def admin_help(update: Update, context: CallbackContext):
    log_interaction(update)

    global admin_user
    if str(update.message.chat_id) != str(admin_user):
        update.message.reply_text("You are not authorized to use this command.")
        return
    else:
        admin_help_text = 'Admin Console\n\n1. Broadcast Message with Image.\n  -/broadcastimage <message> <image_ur>\n2. Broadcast Message without Image.\n  -/broadcast <message>\n3. Send Text to Specific user\n  -/send <user_chat_id> <message>\n4. Delete message sent from users.\n  -/delete <user_chat_id> <message_id>\n5. Verify Broadcasted Message\n -/verify_broadcast.\n6. Delete Broadcasted Message\n-/delete_broadcast\n7. To get Report \n-/info '
        update.message.reply_text(admin_help_text)
def info_data(update: Update, context: CallbackContext):
    branch_counts = 0
    atm_counts = 0
    user_counts = 0
    global admin_user
    with open(BRANCH_DATA_FILE, 'r') as file:
        data = json.load(file)
        branch_counts = len(data['branchs'])
    with open(ATM_DATA_FILE, 'r') as file:
        data = json.load(file)
        atm_counts = len(data['atms'])
    with open(USER_DATA_FILE, 'r') as file:
        data = json.load(file)
        user_counts = len(data)
    if str(update.message.chat_id) != str(admin_user):
        update.message.reply_text("You are not authorized to use this command.")
        return
    else:
         update.message.reply_text('_______________________\nREPORT\n---------------------\nTotal Branch: ' + str(branch_counts) + '\nTotal ATM: ' + str(atm_counts) + '\nTotal Users: ' + str(user_counts))

# Function to handle new users and record their chat ID
def save_user(update: Update, context: CallbackContext):
    log_interaction(update)
    chat_id = update.message.chat_id
    user_name = update.message.chat.username
    user_data[chat_id] = user_name


def handle_message(update: Update, context: CallbackContext) -> None:
    log_interaction(update)
    global bot, lang_to_save, admin_user, formatted_time, lang_perf, user_id_global,lang_id
    if lang_perf == None or lang_perf == '':
        if user_id_global == None or user_id_global =='':
            user_id_global = update.message.chat_id
        xusername =read_user_data(str(user_id_global))
        xusername_splited = xusername.split("+")
        lang_perf = xusername_splited[1]



    user = update.message.from_user
    first_names = user.first_name
    last_names = user.last_name
    user_data = context.user_data
    user_id = update.message.chat_id
    message_id = str(update.message.message_id)
    usernames = user.username
    if first_names == None:
        first_names = '-'
    elif last_names == None:
        last_names = '-'
    elif usernames == None:
        usernames = '-'
    emoji_pattern = re.compile(
        "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F700-\U0001F77F"  # alchemical symbols
        u"\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
        u"\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        u"\U0001FA00-\U0001FA6F"  # Chess Symbols
        u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        u"\U00002702-\U000027B0"  # Dingbats
        u"\U000024C2-\U0001F251"  # Enclosed characters
        "]+", flags=re.UNICODE)
    log_lang = ""
    if lang_perf == "en":
        log_lang = "English"
    elif lang_perf == "oro":
        log_lang = "Afaan Oromoo"
    else:
        log_lang = "Amharic"
    user_message = update.message.text
    clean_message = emoji_pattern.sub(r'', user_message).strip()
    question = clean_message
    logger.info(f"\n Asked Question ******** by {user.username} and  question is {question}  ********")
    user_ids = str(user_id)
    safe_username = usernames.replace("_", "\\_").replace("*", "\\*")

    message_text = f"Log\n________________\nUsername: @" + safe_username + "\nUser Id: `" + user_ids + "`\nMessage Id: `" + message_id + "`\nFirst Name: " + first_names + "\nLast Name: " + last_names + "\nLanguage: " + log_lang + "\nQuest: " + question + "\nTime: " + formatted_time + "\n________________"
    safe_message = message_text.replace("_", "\\_").replace("*", "\\*")
    logger.info(f"Log user excluded safe_text : " + safe_message + "\nAdmin User: " + admin_user)
    context.bot.send_message(chat_id=admin_user, text=safe_message, parse_mode=ParseMode.MARKDOWN)
    language = user_data.get('language', 'en')
    if question == "Start" or question == "Jalqabsiisi" or question == "ጀምር":
        handle_start(update, context)
    elif question == "Language" or question == "Qooqa" or question == "ቋንቋ" or question == "language" or question == "/language":
        lang_id = 1
        lang_to_save = 1
        handle_start(update, context)
    elif question == "Contact Us" or question == "Nu quunnami" or question == "/contact_us" or question == "ያግኙን":
        handle_contact_us(update, context)
    elif question == "FAQ" or question == "Gaaffilee" or question == "/faq" or question == "ጥያቄዎች":
        if lang_perf == 'en':
            question_list(update, context, faq_list, prefix="faquestion_")
        elif lang_perf == 'oro':
             question_list(update, context, faq_list_oro, prefix="faquestion_")
        else:
             question_list(update, context, faq_list_am, prefix="faquestion_")

    elif question == "branch" or question == "Damee":
        search_branch(update, context)
    elif question == "link" or question == "liinki" or question == "Link naf ergi" or question == "link app" or question == "ሊንክ":
        download_app(update, context)
    elif question == "exchange rate" or question == "exchange" or question == "Sharafa":
        exchange_rate(update,context)
    else:
        if lang_perf == 'en':
            answer = find_best_match(context, update, question, qa_pairs_en)
        elif lang_perf == 'oro':
            answer = find_best_match(context, update, question, qa_pairs_oro)
        else:
            answer = find_best_match(context, update, question, qa_pairs_am)
        update.message.reply_text(answer)

def normalize_string(s):
    s = s.lower()
    s = re.sub(r'[^\w\s]', '', s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip()
# Just here is my ATM
def search_atm(update: Update, context: CallbackContext):
    log_interaction(update)
    global lang_perf, user_id_global
    if lang_perf == None or lang_perf == '':
        if user_id_global == None or user_id_global =='':
            user_id_global = update.message.chat_id
        xusername =read_user_data(str(user_id_global))
        xusername_splited = xusername.split("+")
        lang_perf = xusername_splited[1]
    if len(context.args) == 0:
        if lang_perf == 'en':
            update.message.reply_text("Usage: /atm <branch_name> E.g /atm Finfinne")
            return
        elif lang_perf == 'oro':
            update.message.reply_text("Akkaata fayyadamaa:  /atm <maqaa_damee> Fkf. /atm Finfinne")
            return
        else:
            update.message.reply_text("አጠቃቀም፡ /atm <branch_name> E.g /atm Finfinne")
            return

    user_input = ' '.join(context.args).lower()
    normalized_user_input = normalize_string(user_input)
    global lang_faq, lang_to_save
    found_branches = False
    phone_ex = ""
    if lang_perf == "en":
        phone_ex = "To copy the phone number just tap on the number."
    elif lang_perf == "oro":
        phone_ex = "Lakk. Bilbilaa Kophi gochuuf lakkofsichatti yeroo tokko bu'aa."
    else:
        phone_ex = "ስልክ ቁጥሩን ለመያዝ ቁጥሩ ላይ ይንኩ።"

    branch_names = [normalize_string(branch['branch_name']) for branch in atms]
    # best_match, best_score = process.extractOne(normalized_user_input, branch_names, scorer=fuzz.token_sort_ratio)
    best_matches = process.extract(normalized_user_input, branch_names, scorer=fuzz.token_sort_ratio, limit=5)

    for best_match, best_score in best_matches:
        if best_score >= 80:
            found_branches = True
            matching_branch = next(branch for branch in atms if normalize_string(branch['branch_name']) == best_match)

            branch_details_message = (
                f"*Branch Name:* {matching_branch['branch_name']}\n"
                f"*District:* {matching_branch['district']}\n"
                f"*Type:* {matching_branch['type']}\n"
                f"*Phone Number:* `{matching_branch['phone_number']}`\n\n"
                f"{phone_ex}"
            )
            # response_message += branch_details_message
            update.message.reply_text(branch_details_message, parse_mode=ParseMode.MARKDOWN)

            update.message.reply_location(latitude=matching_branch['latitude'], longitude=matching_branch['longitude'])

    if found_branches != True:
        global admin_user
        message_text = update.message.text
        message_text = message_text.replace('/atm ', 'Someone Requested ')
        message_text = message_text + ' ATM.'
        context.bot.send_message(chat_id=admin_user, text=message_text)
        if lang_perf == 'en':
            update.message.reply_text(f"'{user_input}' Branch ATM not found.")
        elif lang_perf == 'oro':
            update.message.reply_text(f"ATM Damee '{user_input}' argachuu hin dandeenye.")
        else:
            update.message.reply_text(f"'{user_input}' ቅርንጫፍ ኤቲኤም አልተገኘም።")

# new one
def search_branch(update: Update, context: CallbackContext):
    log_interaction(update)
    global lang_perf, user_id_global
    if lang_perf == None or lang_perf == '':
        if user_id_global == None or user_id_global =='':
            user_id_global = update.message.chat_id
        xusername =read_user_data(str(user_id_global))
        xusername_splited = xusername.split("+")
        lang_perf = xusername_splited[1]
    if len(context.args) == 0:
        if lang_perf == 'en':
            update.message.reply_text("Usage: /branch <branch_name> E.g /branch Finfinne")
            return
        elif lang_perf == 'oro':
            update.message.reply_text("Akkaata fayyadamaa:  /branch <maqaa_damee> Fkf. /branch Finfinne")
            return
        else:
            update.message.reply_text("አጠቃቀም፡: /branch <branch_name> E.g /branch Finfinne")
            return


    user_input = ' '.join(context.args).lower()
    normalized_user_input = normalize_string(user_input)
    global lang_faq, lang_to_save
    found_branches = False
    phone_ex = ""
    if lang_perf == "en":
        phone_ex = "To copy the phone number just tap on the number."
    elif lang_perf == "oro":
        phone_ex = "Lakk. Bilbilaa Kophi gochuuf lakkofsichatti yeroo tokko bu'aa."
    else:
        phone_ex = "ስልክ ቁጥሩን ለመያዝ ቁጥሩ ላይ ይንኩ።"
    branch_names = [normalize_string(branch['branch_name']) for branch in branchs]
    # best_match, best_score = process.extractOne(normalized_user_input, branch_names, scorer=fuzz.token_sort_ratio)

    best_matches = process.extract(normalized_user_input, branch_names, scorer=fuzz.token_sort_ratio, limit=5)
    for best_match, best_score in best_matches:
        if best_score >= 80:
            found_branches = True
            matching_branch = next(branch for branch in branchs if normalize_string(branch['branch_name']) == best_match)

            branch_details_message = (
                f"*Branch Name:* {matching_branch['branch_name']}\n"
                f"*District:* {matching_branch['district']}\n"
                f"*Type:* {matching_branch['type']}\n"
                f"*Phone Number:* `{matching_branch['phone_number']}`\n\n"
                f"{phone_ex}"
            )
            # response_message += branch_details_message
            update.message.reply_text(branch_details_message, parse_mode=ParseMode.MARKDOWN)

            update.message.reply_location(latitude=matching_branch['latitude'], longitude=matching_branch['longitude'])

    if found_branches != True:
        global admin_user
        message_text = update.message.text
        message_text = message_text.replace('/branch ', 'Someone Requested ')
        message_text = message_text + ' branch.'
        context.bot.send_message(chat_id=admin_user, text=message_text)
        if lang_perf == 'en':
            update.message.reply_text(f"'{user_input}' branch not found.")
        elif lang_perf == 'oro':
            update.message.reply_text(f"Dame '{user_input}' argachuu hin dandeenye.")
        else:
            update.message.reply_text(f"'{user_input}' ቅርንጫፍ አልተገኘም።")



def error_handler(update: Update, context: CallbackContext) -> None:
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

def main():
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("branch", search_branch))
    dispatcher.add_handler(CommandHandler("atm", search_atm))
    dispatcher.add_handler(CommandHandler("download", download_app))
    dispatcher.add_handler(CommandHandler("link", download_app))
    dispatcher.add_handler(CommandHandler("exchange", exchange_rate))
    dispatcher.add_handler(CommandHandler("delete", delete_message))
    dispatcher.add_handler(CommandHandler("delete_broadcast", delete_broadcast))
    dispatcher.add_handler(CommandHandler("verify_broadcast", broadcast_verification))
    dispatcher.add_handler(CommandHandler("admin", admin_help))
    dispatcher.add_handler(CommandHandler("info", info_data))
    dispatcher.add_handler(CommandHandler('send', send_message))
    dispatcher.add_handler(CommandHandler('contact_us', handle_contact_us))
    dispatcher.add_handler(CommandHandler('faq', question_list))
    dispatcher.add_handler(CommandHandler('language', language_selection))
    dispatcher.add_handler(CommandHandler('broadcast', broadcast_message))
    dispatcher.add_handler(CommandHandler('broadcastimage', broadcast_message_image))
    dispatcher.add_handler(CallbackQueryHandler(faq_button_handler, pattern="^faquestion_"))
    dispatcher.add_handler(CallbackQueryHandler(language_selection))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dispatcher.add_error_handler(error_handler)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
