import random

CATASTROPHES = [
    {
        "title": "☢️ Global Yadroviy Qish",
        "desc": "Superdavlatlar o'rtasidagi termoyadro urushidan so'ng atmosferani qalin radioaktiv kul qopladi. Quyosh nuri yerga o'tmaydi, harorat -50°C gacha tushgan. Tashqarida kuchli fon radiatsiyasi va kislotali qor yog'moqda.",
        "duration": "4 yil",
        "req_tags": ["medical", "radiation", "engineer"]
    },
    {
        "title": "🧟‍♂️ 'Korditseps-X' Neyro-Parazit Pandemiyasi",
        "desc": "Biologik laboratoriyadan sizib chiqqan mutatsiyaga uchragan zamburug' sporalari inson asab tizimini egallab, ularni o'ta tajovuzkor va tez harakatlanuvchi mutantlarga aylantirdi. Havo va qon orqali yuqadi.",
        "duration": "3 yil",
        "req_tags": ["bio", "medical", "military"]
    },
    {
        "title": "☄️ 'Apofis-999' Asteroid Zarbasi",
        "desc": "Diametri 6 km bo'lgan ulkan asteroid Tinch okeaniga urildi. Mega-sunami, 9 ballik zilzilalar va vulqonlar otilishi natijasida yer yuzi olov va zaharli oltingugurt gaziga to'ldi.",
        "duration": "5 yil",
        "req_tags": ["engineer", "agri", "craft"]
    },
    {
        "title": "🤖 'Aegis' Sun'iy Intellekt Isyoni",
        "desc": "Global harbiy mudofaa tarmog'i insoniyatni sayyora uchun virus deb topdi. Osmonda avtonom dron-qotillar, yerda esa issiqlik skaneriga ega kibernetik mashinalar har qanday tirik jonni ovlamoqda.",
        "duration": "3 yil",
        "req_tags": ["it", "engineer", "military"]
    },
    {
        "title": "🌊 Buyuk Muzliklar Erishi (Suv To'foni)",
        "desc": "Iqlim falokati tufayli Antarktida va Arktika muzliklari bir necha haftada erib ketdi. Quruqlikning 96 foizi suv ostida qoldi. Yagona najot — suv o'tkazmaydigan germetik yer osti va suv osti bunkerlari.",
        "duration": "6 yil",
        "req_tags": ["engineer", "agri", "psych"]
    },
    {
        "title": "☀️ Quyosh Super-Chaqnashi (Karrington Hodisasi)",
        "desc": "Quyoshdan ajralib chiqqan gigant plazma to'lqini Yer magnitosferasini yorib o'tdi. Dunyodagi barcha elektr tarmoqlari, transformatorlar va elektronika yonib ketdi. Sirtda ultrabinafsha nurlanish o'ta xavfli darajada.",
        "duration": "2 yil",
        "req_tags": ["engineer", "craft", "medical"]
    },
    {
        "title": "🦠 'Qora O'lim 2.0' Sintetik Virusi",
        "desc": "Ginetik modifikatsiyalangan bakteriya 48 soat ichida o'pkani ishdan chiqaradi. Insoniyatning 90 foizi ikki haftada halok bo'ldi. Tashqi havo biologik filtrsiz nafas olish uchun yaroqsiz.",
        "duration": "2 yil",
        "req_tags": ["bio", "medical", "radiation"]
    },
    {
        "title": "🌋 Йelloustoun Super-Vulqoni Otilishi",
        "desc": "Ming yillik uyqudan uyg'ongan super-vulqon atmosferaga milliardlab tonna zaharli kul va oltingugurt dioksidini chiqardi. Nafas olish yo'llari himoyasiz inson 10 daqiqada bo'g'ilib qoladi.",
        "duration": "4 yil",
        "req_tags": ["medical", "agri", "engineer"]
    },
    {
        "title": "👽 Ksenomorf Biologik Bosqini",
        "desc": "Yerga qulagan noma'lum kosmik kema ichidan o'ta tez ko'payuvchi yirtqich organizmlar tarqaldi. Ular tovushga va issiqlikka ta'sirchan bo'lib, zirhli texnikani ham yorib o'ta oladi.",
        "duration": "3 yil",
        "req_tags": ["military", "bio", "it"]
    },
    {
        "title": "🧪 Global Kimyoviy Smog (Zaharli Tuman)",
        "desc": "Harbiy omborlarning zanjirli portlashi oqibatida troposferada og'ir neyro-paralitik gaz bulutlari hosil bo'ldi. Tuman yer yuzasidan 50 metr balandlikkacha cho'kib, barcha o'simlik va hayvonot dunyosini yo'q qildi.",
        "duration": "3 yil",
        "req_tags": ["radiation", "bio", "engineer"]
    }
]

BUNKERS = [
    {
        "name": "Sovet davridagi 'Ob'yekt-84' harbiy bunkeri",
        "size": "150 kv.m",
        "rooms": ["Dizel generator xonasi", "Eski tibbiyot punkti", "Gidroponik issiqxona", "Qurol-yarog' ombori (kodli qulfda)"],
        "supplies": "Konserva, quruq payok va 2 tonna texnik suv bor.",
        "problem": "⚠️ Suv tozalash filtri zanglab ishdan chiqqan va ventilyatsiya quvuridan zaharli havo sizib kirmoqda (Muhandis yoki Texnik kerak).",
        "fix_tags": ["engineer", "craft"]
    },
    {
        "name": "Shveysariya Alp tog'lari ostidagi 'Genesis' Ilmiy Kompleksi",
        "size": "220 kv.m",
        "rooms": ["Biokimyo laboratoriyasi", "Kvant server xonasi", "Krio-uyqu kapsulalari", "Yopiq eko-bog'"],
        "supplies": "Dori-darmonlar mo'l, ammo oziq-ovqat faqat 6 oylik sintetik oqsil paketlaridan iborat.",
        "problem": "⚠️ Bunkerning markaziy kompyuteri va havo haydash tizimi xakerlik virusi tufayli bloklangan (IT/Dasturchi yoki Elektrik kerak).",
        "fix_tags": ["it", "engineer"]
    },
    {
        "name": "Milliarderning 'Eden-VIP' shaxsiy yer osti saroyi",
        "size": "110 kv.m",
        "rooms": ["Kinozal va Bar", "Restoran darajasidagi oshxona", "Alkogol yerto'lasi", "Yotoqxonalar"],
        "supplies": "Delikates ovqatlar va qimmatbaho ichimliklar ko'p, lekin oddiy asbob-uskunalar va dori-darmon deyarli yo'q.",
        "problem": "⚠️ Tashqaridan mutantlar/bosqinchilar asosiy temir eshikni buzishga urinmoqda, mudofaa tizimi yo'q (Harbiy/Qurol yoki Muhandis kerak).",
        "fix_tags": ["military", "craft"]
    },
    {
        "name": "Arktika muzliklari ostidagi 'Urug'lar Xazinasi' bunkeri",
        "size": "180 kv.m",
        "rooms": ["Botanika laboratoriyasi", "Muzlatkich omborlar", "Geotermal isitish stansiyasi", "Kutubxona"],
        "supplies": "Millionlab o'simlik urug'lari bor, ammo tayyor yegulik juda kam.",
        "problem": "⚠️ Isitish qozoni bosimi tushib ketgan, harorat pasaymoqda va tez orada urug'lardan hosil olish tizimini yo'lga qo'yish shart (Agronom va Muhandis kerak).",
        "fix_tags": ["agri", "engineer"]
    },
    {
        "name": "Metro-2 Chuqur Yer Osti Stansiyasi",
        "size": "250 kv.m",
        "rooms": ["Temiryo'l vagoni (turar joy)", "Qo'lbola lazaret", "Qo'ziqorin yetishtirish fermasi", "Dizel deposi"],
        "supplies": "Ko'p miqdorda konserva, filtrlar va pulemyot o'qlari bor.",
        "problem": "⚠️ Bunkerga noma'lum infeksiya sporalari kirib qolgan, havo dezinfeksiya qilinmasa hamma kasallanadi (Shifokor yoki Mikrobiolog kerak).",
        "fix_tags": ["medical", "bio"]
    },
    {
        "name": "Tinch okeani tubidagi 'Nautilus' suv osti stansiyasi",
        "size": "130 kv.m",
        "rooms": ["Kapitan ko'prikchasi", "Kislorod elektroliz xonasi", "Suv o'tlari fermasi", "Boshqaruv bloki"],
        "supplies": "Dengiz mahsulotlari va toza suv generatori mavjud.",
        "problem": "⚠️ Suv bosimi tufayli 3-bo'lma korpusida yoriq paydo bo'lgan, payvandlash va mustahkamlash zarur (Payvandchi/Usta yoki Arxitektor kerak).",
        "fix_tags": ["craft", "engineer"]
    }
]

RANDOM_EVENTS = [
    "⚡ <b>FAVQULODDA HODISA:</b> Bunker generatorida qisqa tutashuv yuz berdi! Muhandislik va texnik ko'nikmaga ega o'yinchilarning qadri yanada oshdi.",
    "🐀 <b>FAVQULODDA HODISA:</b> Oziq-ovqat omboriga zaharli kemiruvchilar kirib, zaxiraning 30 foizini yaroqsiz holga keltirdi! Oshpaz va Agronomlarga ehtiyoj kuchaydi.",
    "📡 <b>FAVQULODDA HODISA:</b> Tashqaridan SOS signali va harbiy qaroqchilar guruhi yaqinlashayotgani haqida radioxabar tutildi! Qurol va himoyachilar juda muhim.",
    "🦠 <b>FAVQULODDA HODISA:</b> Ventilyatsiya shaxtasida mog'or va bakteriyalar ko'paya boshladi! Tibbiyot va biologiya mutaxassislari bo'lmasa xavf yuqori.",
    "🧠 <b>FAVQULODDA HODISA:</b> Yopiq makon va qorong'ulik tufayli jamoada kuchli vahima (panika) boshlanmoqda! Ruhiy barqaror va diplomat insonlar kerak.",
    "💧 <b>FAVQULODDA HODISA:</b> Ichimlik suvi quvurida radiatsiya qoldiqlari aniqlandi! Suvni tekshirish va filtrlash vositalari hayot-mamot masalasiga aylandi."
]

# Kasblar va ularning teglari (Epilogda hisoblash uchun)
PROFESSIONS = [
    ("Jarroh-travmatolog", "medical"), ("Harbiy dala shifokori", "medical"), ("Feldsher-reanimatolog", "medical"),
    ("Farmatsevt-kimyogar", "medical"), ("Klinik psixolog-psixoterapevt", "psych"), ("Veterinar-jarroh", "medical"),
    ("Mikrobiolog-virusolog", "bio"), ("Genetik-biolog", "bio"), ("Kimyogar-toksikolog", "radiation"),
    ("Yadro fizigi (Radiolog)", "radiation"), ("Agronom-seleksioner", "agri"), ("Gidroponika muhandisi", "agri"),
    ("Botanik-ekolog", "agri"), ("Muhandis-energetik", "engineer"), ("Muhandis-mexanik", "engineer"),
    ("Santexnik va suv tizimlari ustasi", "engineer"), ("Arxitektor-quruvchi", "engineer"), ("Tokar-frezerchi", "craft"),
    ("Avtomexanik-payvandchi", "craft"), ("Slesar-chilangar", "craft"), ("Elektromontyor", "engineer"),
    ("Kiberxavfsizlik mutaxassisi (Pentester)", "it"), ("Tizim administratori (DevOps)", "it"), ("Robototexnika muhandisi", "it"),
    ("Radioaloqa muhandisi", "it"), ("Maxsus kuchlar zobiti (Snayper)", "military"), ("Harbiy sapyor-muhandis", "military"),
    ("Politsiya detektivi", "military"), ("O't o'chiruvchi-qutqaruvchi", "military"), ("Professional tansoqchi", "military"),
    ("Bosh oshpaz (Oziq-ovqat texnologi)", "agri"), ("Qassob va ovchi", "agri"), ("Tikuvchi-hunarmand", "craft"),
    ("Geolog-konchi", "craft"), ("Professional diplomat", "psych"), ("Tarixchi-arxeolog", "none"),
    ("TikTok bloger (3 mln obunachi)", "none"), ("Kripto-treyder", "none"), ("Astrolog-tarolog", "none"),
    ("Stand-up komik", "psych"), ("Sobiq sudya", "psych"), ("Buxgalter-auditor", "none"),
    ("Kibersportchi (CS2 chempioni)", "none"), ("Professional bokschi", "military"), ("Tatuirovka ustasi", "none"),
    ("Somelye (Vino eksperti)", "none"), ("Falsafa professori", "psych"), ("Ko'chmas mulk rieltori", "none")
]

CARDS_POOL = {
    "salomatlik": [
        "Mutlaqo sog'lom (Temir immunitet)", "Mutlaqo sog'lom", "Mutlaqo sog'lom (Sportchi yuragi)",
        "Nur kasalligi (1-bosqich, dori bilan tuzaladi)", "Bronxial astma (Ingalyator bo'lmasa bo'g'iladi)",
        "Qandli diabet (1-toifa, insulinga bog'liq)", "Qandli diabet (2-toifa, parhez talab qiladi)",
        "O'ng qulog'i kar (Portlash kontuziyasi)", "Ko'rish qobiliyati past (-5.5, ko'zoynaksiz ko'rmaydi)",
        "Yashirin formadagi sil (Immunitet tushsa yuqumli shaklga o'tadi)", "Epilepsiya (Kuchli stress va chiroqda tutqanoq tutadi)",
        "Gepatit B (Faqat qon orqali yuqadi)", "Yurak aritmiyasi (Og'ir jismoniy mehnat mumkin emas)",
        "Chap oyog'ida bionik titan protez", "Surunkali migren (Ba'zan 1 kun bosh og'rig'idan tura olmaydi)",
        "Kuchli allergiya (Antibiotiklar va changga)", "Umurtqa churrasi (Grijasi bor, 5 kg dan og'ir ko'tarolmaydi)",
        "Gemofiliya (Qon ivimasligi — har qanday kesilish xavfli)", "Bipolyar buzilish (Kayfiyati depressiyadan eyforiyaga o'ynaydi)",
        "Oshqozon yarasi (Quruq va achchiq ovqat yeya olmaydi)", "Yaqinda ko'richak operatsiyasi bo'lgan (Choklari hali bitmagan)",
        "O'ng qo'lining 3 ta barmog'i yo'q", "Surunkali bronxit (Tinmay balg'amli yo'taladi, lekin yuqumli emas)",
        "Daltonizm (Ranglarni ajrata olmaydi)", "Gipertoniya (Qon bosimi 180/110 ga chiqib ketadi)"
    ],
    "tana": [
        "Atletik, mushakdor (85 kg)", "Skelet kabi o'ta ozg'in (48 kg)", "To'ladan kelgan, qorin qo'ygan (98 kg)",
        "Sportchi qomat, o'ta chidamli", "O'rtacha, biroz bukchaygan", "Novcha (195 sm) va keng yelkali",
        "Past bo'yli (158 sm), lekin juda chaqqon", "Semiz (128 kg, tez hansiraydi va ko'p ovqat yeydi)",
        "Nozik va egiluvchan (Tor joylardan bemalol o'tadi)", "Baquvvat, qadoq qo'lli", "Biroz oqsoqlanib yuradi",
        "Chiniqqan, sovuqqa va ochlikka chidamli"
    ],
    "xususiyat": [
        "Mohir diplomat (Har qanday janjalni tinchitadi)", "O'ta sovuqqon, qon va o'limdan aslo qo'rqmaydi",
        "Fenomenal fotografik xotira (Ko'rgan kitobini yodlab oladi)", "Tabiiy lider, odamlarni o'z ortidan ergashtira oladi",
        "Analitik aql, sovuq va aniq hisob-kitob", "Xushchaqchaq, eng og'ir kunda ham jamoa ruhini ko'taradi",
        "Yolg'onni tana tilidan va ovozdan darhol sezadi", "Tug'ma optimist, hech qachon tushkunlikka tushmaydi",
        "Sinik va pragmatist (Umumiy manfaat uchun kuchsizlarni qurbon qila oladi)", "O'ta ehtiyotkor va shubhachi",
        "Xarizmatik notiq (Odamlarni istalgan narsaga ishontira oladi)", "Oltinchi hissiyot (Xavfni oldindan sezadi)",
        "Mehnatsevar (Kuniga 16 soat tinimsiz ishlay oladi)", "Tejamkor (1 haftalik ovqatni 3 haftaga yetkazadi)"
    ],
    "xobbi": [
        "Zaharlarni va dorivor giyohlarni o'rganish", "Gidroponika va uy sharoitida qo'ziqorin yetishtirish",
        "Qulfbuzarlik (Lockpicking) va seyflarni ochish", "Ovchilik va yovvoyi tabiatda omon qolish (Bushkraft)",
        "Radiotexnika, ratsiya va sxemalar lehimlash", "Shaxmat (Xalqaro master darajasi)",
        "Akustik gitara chalish va qo'shiq aytish", "Yog'och va metalldan qurol/asbob yasash",
        "Sharq yakkakurashlari va pichoqbozlik (Krav-Maga)", "Uy sharoitida spirt, pivo va vino tayyorlash",
        "Kibersport va dronlarni boshqarish", "Astrologiya, numerologiya va Tarot kartalari",
        "Birinchi tibbiy yordam va massaj kurslari", "Pazandachilik va konserva yopish",
        "Krossvord va kriptografik shifrlarni yechish", "Tikuvchilik va poyabzal ta'mirlash"
    ],
    "fobiya": [
        "Avtofobiya (Yolg'iz qolishdan vahima)", "Klaustrofobiya (Tor va yopiq xonalarda bo'g'ilib qolish hissi)",
        "Niktofobiya (Qorong'ulikda vahimaga tushib baqiradi)", "Araxnofobiya (O'rgimchak va hasharotlardan o'lgudek qo'rqish)",
        "Mizofobiya (Mikrob, chang va ifloslanishdan jirkanish)", "Gemofobiya (Qon ko'rsa boshi aylanib hushidan ketadi)",
        "Akrofobiya (Balandlikdan qo'rqish)", "Pirofobiya (Olov va tutundan vahima)",
        "Fobiya yo'q (Asablari po'latdek mustahkam)", "Fobiya yo'q",
        "Tafofobiya (Yer ostida tiriklayin ko'milishdan qo'rqish)", " Fonofobiya (Kuchli va kutilmagan tovushlardan qotib qoladi)",
        "Iatrobobiya (Shifokorlar va ukol ignasidan qo'rqish)", "Gidrofobiya (Chuqur suv va cho'kishdan qo'rqish)"
    ],
    "zaiflik": [
        "Kleptomaniya (Boshqalarning mayda buyumlarini sezdirmay o'g'irlaydi)", "Nikotinga kuchli qaramlik (Sigaret bo'lmasa tajovuzkor bo'lib qoladi)",
        "Alkogolga moyillik (Stressni faqat ichkilik bilan yengadi)", "O'ta o'jar, xatosini hech qachon tan olmaydi",
        "Qiziqqon va agressiv (Arzimagan gapga mushtlashib ketadi)", "G'iybatchi, sirlarni umuman saqlay olmaydi",
        "Insomniya (Uyqu dori ichmasa 3 kunlab uxlolmaydi)", "Pedant (Hamma narsa chizig'ida turmasa janjal qiladi)",
        "Qimorboz (Hatto oziq-ovqat payokini ham garovga tikadi)", "Xudbin (Xavf tug'ilsa faqat o'z jonini o'ylaydi)",
        "Ochko'z (Stress payti kechasi yashirincha ko'p ovqat yeb qo'yadi)", "Yolg'onchi (Odat bo'yicha bo'rttirib va aldab gapiradi)",
        "Dangasa (Majburlamasa og'ir ishga qo'l urmaydi)", "Jiddiy zaifligi yo'q (Tartibli inson)"
    ],
    "jihoz": [
        "Suv va havoni zahar hamda radiatsiyaga tekshirish laboratoriyasi", "Jarrohlik asboblari, kichik defibrillyator va antibiotiklar jamlanmasi",
        "30 xil yuqori hosilli sabzavot, kartoshka va bug'doy urug'lari konteyneri", "Yig'ma quyosh paneli (200W), akkumulyator va invertor",
        "Kalashnikov avtomati (AK-74) va 120 ta o'q", "Makarov pistoleti va 32 ta o'q",
        "Ko'chma biokimyoviy mikroskop va vaksina reaktivlari", "Gazli gorelka, 8 ta propan baloni va qozon",
        "Bunkerning maxfiy arxitektura chizmalari va barcha eshiklar master-kodi", "16 TB himoyalangan SSD (Butun insoniyat tibbiy, texnik va ilmiy ensiklopediyalari)",
        "Dozimetr (Radiatsiya o'lchagich) va 3 ta 'Ximzashita' (OZK) himoya kostyumi", "Professional payvandlash apparati va slesarlik asboblari chamadoni",
        "4 ta uzoq masofali harbiy shifrlangan ratsiya", "Sanoat darajasidagi teskari osmos suv tozalash filtri",
        "Kvadrokopter dron (Tungi termal kamerasi bilan)", "Mexanik qo'l generatori (Dinamo-mashina)"
    ],
    "ryukzak": [
        "O'tkir titan bolta, chaqmoqtosh va kompas", "5 blok sigareta va 10 ta Benzinli Zippo zajigalkasi",
        "5 litr 96% li toza tibbiyot spirti", "Leatherman multituli, lehimlagich, qalay va kanifol",
        "15 quti harbiy quruq payok (MRE - 1 oyga yetadi)", "30 ta FFP3 respirator va 500 ta suv tozalovchi xlor tabletkasi",
        "Akustik gitara, shaxmat taxtasi va qarta", "Lazerli masofa o'lchagich va 50 metr po'lat tros",
        "Zirhli noutbuk (Kali Linux va xakerlik dasturlari bilan) + quyosh poverbanki", "1 yillik tinchlantiruvchi, uyqu va kuchli og'riq qoldiruvchi dorilar",
        "Ov arbaleti (20 ta po'lat paykoni bilan) va tungi durbin", "10 kg shakar, 5 kg tuz va 20 quti choy/qahva",
        "3 ta issiq arktika uyqu qopi (Spalniy meshok) va palatka", "Tikuv to'plami, 5 juft harbiy etik va issiq kiyimlar",
        "100 ta sham, 5 ta fonarik va 50 ta batareyka"
    ],
    "konikma": [
        "Ushbu bunkerning maxfiy omborxonasi kalit-kartasiga ega", "Og'ir jarohatlarni operatsiya qilish va suyaklarni tiklash",
        "Tuproqsiz va quyoshsiz sharoitda sun'iy yorug'likda hosil yetishtirish", "Har qanday dizel generator, nasos va elektr tarmog'ini noldan tiklash",
        "Qurolsiz jang ustasi va bunker eshiklariga mudofaa tuzoqlarini o'rnatish", "Zaharlar, radiatsiya va viruslarga qarshi antidot tayyorlash",
        "Muddati o'tgan yoki yovvoyi masalliqlardan ham xavfsiz va to'yimli ovqat pishirish", "Buzilgan ventilyatsiya va suv filtrlash tizimini qo'lbola vositalardan yig'ish",
        "Har qanday elektron qulf, server va xavfsizlik tizimini buzib kirish (Xaking)", "Jamoada psixologik inqiroz, suiqasd va janjallarning oldini olish",
        "Metall eritish, payvandlash va qurol-aslaha ta'mirlash", "Tashqi razvedka: radiatsiyali va xavfli hududda izsiz harakatlanish"
    ],
    "maxsus": [
        {"id": "heal", "text": "💉 <b>Panatseya:</b> Istalgan o'yinchining (yoki o'zingizning) Salomatligini 'Mutlaqo sog'lom' holatiga o'zgartirish"},
        {"id": "spy", "text": "🕵️‍♂️ <b>Detektiv:</b> Istalgan o'yinchining bitta yashirin kartasini hamma uchun majburan fosh qilish"},
        {"id": "reroll_job", "text": "🔄 <b>Qayta tayyorlov:</b> Istalgan o'yinchining Kasbini tasodifiy yangisiga almashtirib yuborish"},
        {"id": "cure_phobia", "text": "🧠 <b>Psixoterapiya:</b> Istalgan o'yinchining Fobiya va Zaifligini butunlay bartaraf etish"},
        {"id": "steal_bag", "text": "🎒 <b>Talonchilik:</b> Boshqa o'yinchining 9-Jihozini o'zingiznikiga olib qo'yish (unda oddiy fonarik qoladi)"},
        {"id": "swap_health", "text": "🔀 <b>Taqdir almashinuvi:</b> O'zingizning Salomatlik kartangizni boshqa o'yinchiniki bilan almashtirish"},
        {"id": "shield", "text": "🛡 <b>Bunker Immuniteti:</b> Keyingi ovoz berish bosqichida tanlangan o'yinchiga qarshi hech kim ovoz bera olmaydi"},
        {"id": "double_vote", "text": "⚖️ <b>Avtoritet:</b> Keyingi ovoz berishda tanlangan o'yinchining (yoki o'zingizning) ovozingiz 2 ta ovozga teng bo'ladi"},
        {"id": "rejuvenate", "text": "🧬 <b>Genetik yangilanish:</b> Tanlangan o'yinchining Biologiyasini '24 yosh, sog'lom va nasl qoldira oladi' holatiga o'tkazish"}
    ]
}

CARD_LABELS = {
    "kasb": "1. Kasb",
    "bio": "2. Biologiya",
    "salomatlik": "3. Salomatlik",
    "tana": "4. Tana tuzilishi",
    "xususiyat": "5. Xususiyat",
    "xobbi": "6. Xobbi",
    "fobiya": "7. Fobiya",
    "zaiflik": "8. Zaiflik",
    "jihoz": "9. Jihozlar",
    "ryukzak": "10. Ryukzak",
    "konikma": "11. Ko'nikma",
    "maxsus": "12. Maxsus xarita"
}


def generate_character(used_professions: list) -> dict:
    """Takrorlanmas kasb, tajriba yili, nasl qoldirish holati va balanslangan xususiyatlar generatori"""
    available = [p for p in PROFESSIONS if p[0] not in used_professions]
    if not available:
        available = PROFESSIONS

    job_title, job_tag = random.choice(available)
    used_professions.append(job_title)

    gender = random.choice(["Erkak", "Ayol"])
    age = random.randint(19, 64)
    exp_years = max(1, min(age - 18, random.randint(1, 25)))

    # Nasl qoldirish qobiliyati yoshga va tasodifga qarab
    if age > 52 and gender == "Ayol":
        fertility = "Farzand ko'ra olmaydi (Yosh tufayli)"
        fertile_bool = False
    elif random.random() < 0.22:
        fertility = "Bepusht (Farzand ko'ra olmaydi)"
        fertile_bool = False
    else:
        fertility = "Sog'lom, nasl qoldira oladi"
        fertile_bool = True

    spec = random.choice(CARDS_POOL["maxsus"])

    return {
        "kasb": {"val": f"{job_title} (Tajriba: {exp_years} yil)", "tag": job_tag, "opened": False},
        "bio": {"val": f"{gender}, {age} yoshda — {fertility}", "gender": gender, "fertile": fertile_bool, "opened": False},
        "salomatlik": {"val": random.choice(CARDS_POOL["salomatlik"]), "opened": False},
        "tana": {"val": random.choice(CARDS_POOL["tana"]), "opened": False},
        "xususiyat": {"val": random.choice(CARDS_POOL["xususiyat"]), "opened": False},
        "xobbi": {"val": random.choice(CARDS_POOL["xobbi"]), "opened": False},
        "fobiya": {"val": random.choice(CARDS_POOL["fobiya"]), "opened": False},
        "zaiflik": {"val": random.choice(CARDS_POOL["zaiflik"]), "opened": False},
        "jihoz": {"val": random.choice(CARDS_POOL["jihoz"]), "opened": False},
        "ryukzak": {"val": random.choice(CARDS_POOL["ryukzak"]), "opened": False},
        "konikma": {"val": random.choice(CARDS_POOL["konikma"]), "opened": False},
        "maxsus": {"val": spec["text"], "code": spec["id"], "opened": False, "used": False}
    }


def generate_epilogue(game: dict, survivors: list) -> str:
    """O'yin yakunida bunkerga kirganlar omon qoldimi yoki yo'qmi — tahliliy hikoya yaratish"""
    bunk = game["bunker"]
    cat = game["catastrophe"]
    tags = set(p["cards"]["kasb"].get("tag", "none") for p in survivors)

    # 1. Bunker muammosi hal bo'ldimi?
    fixed_problem = any(t in tags for t in bunk["fix_tags"])
    # 2. Falokatga mos mutaxassislar bormi?
    matched_cat = sum(1 for t in cat["req_tags"] if t in tags)
    # 3. Nasl davom etadimi? (Kamida 1 ta nasl qoldira oladigan Erkak va 1 ta Ayol)
    fertile_men = sum(1 for p in survivors if p["cards"]["bio"].get("gender") == "Erkak" and p["cards"]["bio"].get("fertile"))
    fertile_women = sum(1 for p in survivors if p["cards"]["bio"].get("gender") == "Ayol" and p["cards"]["bio"].get("fertile"))
    can_reproduce = (fertile_men >= 1 and fertile_women >= 1)

    story = ["📜 <b>YAKUNIY EPILOG: BUNKER TAQDIRI</b>\n━━━━━━━━━━━━━━━━━━"]

    if fixed_problem:
        story.append("✅ <b>Texnik holat:</b> Jamoadagi mutaxassislar bunkerning asosiy muammosini o'z vaqtida bartaraf etishdi. Tizimlar barqaror ishladi.")
    else:
        story.append("❌ <b>Texnik halokat:</b> Afsuski, bunkerga kirganlar orasida bunkerning asosiy nosozligini tuzata oladigan mutaxassis topilmadi. Bir necha oydan so'ng tizim ishdan chiqib, jamoa og'ir talafot ko'rdi.")

    if matched_cat >= 2:
        story.append(f"🌟 <b>Omon qolish:</b> Jamoa <i>'{cat['title']}'</i> sharoitiga juda mos edi. Ular {cat['duration']} davomida barcha xavflarni yengib o'tishdi.")
    elif matched_cat == 1:
        story.append(f"⚠️ <b>Qiyinchilik bilan omon qolish:</b> Jamoa katta qiyinchiliklar, ochlik va kasalliklar bilan bo'lsa-da, {cat['duration']} muddatni boshdan kechirdi.")
    else:
        story.append("💀 <b>Biologik va tashqi xavf:</b> Jamoada na shifokor va na muhim mutaxassislar yetarli bo'lgani sababli, ular belgilangan muddat oxirigacha yetib bora olishmadi.")

    if can_reproduce:
        story.append("👶 <b>Insoniyat kelajagi:</b> Bunkerdan chiqqach, omon qolganlar yangi avlodni dunyoga keltirishdi va yangi sivilizatsiyaga asos solishdi!")
    else:
        story.append("🥀 <b>Demografik inqiroz:</b> Jamoa omon qolgan bo'lsa-da, ular orasida farzand ko'ra oladigan juftlik yo'qligi sababli insoniyat nasli shu yerda uzildi...")

    return "\n\n".join(story)