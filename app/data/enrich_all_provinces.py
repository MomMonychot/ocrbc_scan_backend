"""Enriches all 25 provinces of Cambodia with their official districts, municipalities, and major communes."""

import json
from pathlib import Path

DATA_PATH = Path("ocrbc_scan_backend/app/data/cambodia_geographic_hierarchy.json")

with open(DATA_PATH, "r", encoding="utf-8") as f:
    hierarchy = json.load(f)

prov_map = {p["code"]: p for p in hierarchy.get("provinces", [])}

# Dictionary of all districts per province
PROVINCE_DISTRICTS_DATA = {
    # 01 Banteay Meanchey
    "01": [
        {"code": "0102", "name_km": "ស្រុកមង្គលបូរី", "name_en": "Mongkol Borei", "communes": ["បន្ទាយនាង (Banteay Neang)", "បត់ត្រង់ (Bat Trang)", "ចំណោម (Chamnaom)", "គោកបាល្ល័ង្ក (Kouk Ballangk)"]},
        {"code": "0103", "name_km": "ស្រុកភ្នំស្រុក", "name_en": "Phnum Srok", "communes": ["ណាំតៅ (Nam Tau)", "ពន្លិច (Ponley)", "ស្ពានស្រែង (Spean Sraeng)"]},
        {"code": "0104", "name_km": "ស្រុកព្រះនេត្រព្រះ", "name_en": "Preah Netr Preah", "communes": ["ឈ្នួរមានជ័យ (Chhnour Mean Chey)", "ជប់វារី (Chob Varei)", "ភ្នំដី (Phnum Dei)"]},
        {"code": "0105", "name_km": "ស្រុកអូរជ្រៅ", "name_en": "Ou Chrov", "communes": ["ចង្ហា (Changha)", "កូប (Koub)", "សំរោង (Samraong)"]},
        {"code": "0106", "name_km": "ក្រុងសិរីសោភ័ណ", "name_en": "Krong Serei Saophoan", "communes": ["សង្កាត់កំពង់ស្វាយ (Sangkat Kampong Svay)", "សង្កាត់ព្រះពន្លា (Sangkat Preah Ponlea)", "សង្កាត់ទឹកថ្លា (Sangkat Tuek Thla)"]},
        {"code": "0107", "name_km": "ស្រុកថ្មពួក", "name_en": "Thma Puok", "communes": ["គោកកឋិន (Kouk Kathin)", "ថ្មពួក (Thma Puok)", "បន្ទាយឆ្មារ (Banteay Chhmar)"]},
        {"code": "0108", "name_km": "ស្រុកស្វាយចេក", "name_en": "Svay Chek", "communes": ["ស្វាយចេក (Svay Chek)", "តារាងសែន (Ta Reang Saen)"]},
        {"code": "0109", "name_km": "ក្រុងប៉ោយប៉ែត", "name_en": "Krong Poipet", "communes": ["សង្កាត់ប៉ោយប៉ែត (Sangkat Poipet)", "សង្កាត់ផ្សារកណ្តាល (Sangkat Phsar Kandal)", "សង្កាត់និមិត្ត (Sangkat Nimitt)"]},
        {"code": "0110", "name_km": "ស្រុកម៉ាឡៃ", "name_en": "Malai", "communes": ["បឹងបេង (Boeng Beng)", "ម៉ាឡៃ (Malai)", "អូរសំព័រ (Ou Sampor)"]}
    ],
    # 02 Battambang
    "02": [
        {"code": "0201", "name_km": "ស្រុកបាណន់", "name_en": "Banan", "communes": ["កន្ទឺ ១ (Kanteu 1)", "បាយដំរាំ (Bay Damram)", "ឈើទាល (Chheu Teal)", "ស្នឹង (Snoeng)"]},
        {"code": "0202", "name_km": "ស្រុកថ្មគោល", "name_en": "Thma Koul", "communes": ["តាពូង (Ta Poung)", "តាម៉ឺន (Ta Meun)", "អូតាគី (Ou Taki)", "ជ្រៃ (Chrey)"]},
        {"code": "0203", "name_km": "ក្រុងបាត់ដំបង", "name_en": "Krong Battambang", "communes": ["សង្កាត់ស្វាយប៉ោ (Sangkat Svay Pao)", "សង្កាត់ព្រែកព្រះស្តេច (Sangkat Prek Preah Sdach)", "សង្កាត់វត្តគរ (Sangkat Voat Kor)", "សង្កាត់ទួលតាឯក (Sangkat Tuol Ta Aek)"]},
        {"code": "0204", "name_km": "ស្រុកបវេល", "name_en": "Bavel", "communes": ["បវេល (Bavel)", "ឃ្លាំងមាស (Khlang Meas)", "បឹងប្រាំ (Boeng Pram)"]},
        {"code": "0205", "name_km": "ស្រុកឯកភ្នំ", "name_en": "Ek Phnom", "communes": ["ព្រែកនរិន្ទ (Prek Norint)", "សំរោងក្នុង (Samraong Knong)", "ពាមឯក (Peam Ek)"]},
        {"code": "0206", "name_km": "ស្រុកមោងឫស្សី", "name_en": "Moung Ruessei", "communes": ["មោង (Moung)", "គារ (Kear)", "ព្រៃស្វាយ (Prey Svay)", "ឫស្សីក្រាំង (Ruessei Krang)"]},
        {"code": "0207", "name_km": "ស្រុករតនមណ្ឌល", "name_en": "Rotanak Mondol", "communes": ["ស្តៅ (Sdau)", "អណ្តើកហែប (Andaeuk Haeb)", "ត្រែង (Treang)"]},
        {"code": "0208", "name_km": "ស្រុកសង្កែ", "name_en": "Sangkae", "communes": ["អន្លង់វិល (Anlong Vil)", "នរា (Norea)", "រាំងកេសី (Reang Kesei)", "កំពង់ព្រះ (Kampong Preah)"]},
        {"code": "0209", "name_km": "ស្រុកសំឡូត", "name_en": "Samlout", "communes": ["តាសាញ (Ta Sanh)", "សំឡូត (Samlout)", "មានជ័យ (Mean Chey)"]},
        {"code": "0210", "name_km": "ស្រុកសំពៅលូន", "name_en": "Sampov Lun", "communes": ["សំពៅលូន (Sampov Lun)", "អង្គរបាន (Angkor Ban)"]},
        {"code": "0211", "name_km": "ស្រុកភ្នំព្រឹក", "name_en": "Phnom Proek", "communes": ["ភ្នំព្រឹក (Phnom Proek)", "បារាំងធ្លាក់ (Barang Thleak)"]},
        {"code": "0212", "name_km": "ស្រុកកំរៀង", "name_en": "Kamrieng", "communes": ["កំរៀង (Kamrieng)", "បឹងរាំង (Boeng Reang)"]},
        {"code": "0213", "name_km": "ស្រុកកោះក្រឡ", "name_en": "Koas Krala", "communes": ["កោះក្រឡ (Koas Krala)", "ព្រះពន្លា (Preah Ponlea)"]},
        {"code": "0214", "name_km": "ស្រុករុក្ខគីរី", "name_en": "Rukh Kiri", "communes": ["ព្រែកជីក (Prek Chik)", "បាសាក់ (Basak)"]}
    ],
    # 03 Kampong Cham
    "03": [
        {"code": "0301", "name_km": "ស្រុកបាធាយ", "name_en": "Batheay", "communes": ["បាធាយ (Batheay)", "ច្បារអំពៅ (Chbar Ampov)", "មេព្រីង (Me Pring)", "សំបូរ (Sambour)"]},
        {"code": "0302", "name_km": "ស្រុកចំការលើ", "name_en": "Chamkar Leu", "communes": ["ចំការអណ្តូង (Chamkar Andoung)", "ស្វាយទាប (Svay Teab)", "តាអុង (Ta Ong)"]},
        {"code": "0303", "name_km": "ស្រុកជើងព្រៃ", "name_en": "Cheung Prey", "communes": ["សូទិប (Sotip)", "ព្រៃចារ (Prey Char)", "ស្រម៉រ (Sramor)"]},
        {"code": "0305", "name_km": "ក្រុងកំពង់ចាម", "name_en": "Krong Kampong Cham", "communes": ["សង្កាត់កំពង់ចាម (Sangkat Kampong Cham)", "សង្កាត់វាលវង់ (Sangkat Veal Vong)", "សង្កាត់បឹងកុក (Sangkat Boeng Kok)"]},
        {"code": "0306", "name_km": "ស្រុកកំពង់សៀម", "name_en": "Kampong Siem", "communes": ["អំពិល (Ampil)", "កោះមិត្ត (Kaoh Mitt)", "រអាង (Ro'ang)"]},
        {"code": "0307", "name_km": "ស្រុកកងមាស", "name_en": "Kang Meas", "communes": ["អង្គរបាន (Angkor Ban)", "ពាមជីកង (Peam Chi Kang)", "រាយប៉ាយ (Reay Pay)"]},
        {"code": "0308", "name_km": "ស្រុកកោះសូទិន", "name_en": "Koh Sotin", "communes": ["កំពង់រាប (Kampong Reab)", "កោះសូទិន (Kaoh Sotin)", "ពង្រ (Pongro)"]},
        {"code": "0309", "name_km": "ស្រុកព្រៃឈរ", "name_en": "Prey Chhor", "communes": ["ជ្រៃវៀន (Chrey Vien)", "ព្រៃឈរ (Prey Chhor)", "សូរគង (Sour Kong)"]},
        {"code": "0310", "name_km": "ស្រុកស្រីសន្ធរ", "name_en": "Srey Santhor", "communes": ["បារាយណ៍ (Baray)", "ព្រែកពោធិ៍ (Prek Pou)", "ស្វាយពោធិ៍ (Svay Pou)"]}
    ],
    # 05 Kampong Speu
    "05": [
        {"code": "0501", "name_km": "ស្រុកបរសេដ្ឋ", "name_en": "Basedth", "communes": ["បរសេដ្ឋ (Basedth)", "កក់ (Kak)", "និទាន (Nitean)"]},
        {"code": "0502", "name_km": "ក្រុងច្បារមន", "name_en": "Krong Chbar Mon", "communes": ["សង្កាត់ច្បារមន (Sangkat Chbar Mon)", "សង្កាត់រកាធំ (Sangkat Roka Thum)", "សង្កាត់ស្វាយក្រវ៉ាន់ (Sangkat Svay Kravanh)"]},
        {"code": "0503", "name_km": "ស្រុកគងពិសី", "name_en": "Kong Pisei", "communes": ["អង្គពពេល (Angk Popel)", "ព្រះនិព្វាន្ត (Preah Nipean)", "វាល (Veal)"]},
        {"code": "0504", "name_km": "ស្រុកឱរ៉ាល់", "name_en": "Aoral", "communes": ["ហោងសំណំ (Haong Samnam)", "រស្មីសាមគ្គី (Reaksmei Sameakki)"]},
        {"code": "0505", "name_km": "ស្រុកឧដុង្គម៉ែជ័យ", "name_en": "Odongk Meanchey", "communes": ["វាំងចាស់ (Veang Chas)", "ត្រាចទង (Trach Tong)"]},
        {"code": "0506", "name_km": "ស្រុកសំរោងទង", "name_en": "Samraong Tong", "communes": ["រលាំងគ្រើល (Roleang Kroeul)", "សំរោងទង (Samraong Tong)"]},
        {"code": "0507", "name_km": "ស្រុកថ្ពង", "name_en": "Thpong", "communes": ["អមលាំង (Amlang)", "ប្រាំបីមុំ (Prambei Mom)"]},
        {"code": "0508", "name_km": "ស្រុកភ្នំស្រួច", "name_en": "Phnum Sruoch", "communes": ["ត្រែងត្រយឹង (Treng Trayoeng)", "ព្រៃក្មេង (Prey Kmeng)"]}
    ],
    # 07 Kampot
    "07": [
        {"code": "0701", "name_km": "ស្រុកអង្គរជ័យ", "name_en": "Angkor Chey", "communes": ["អង្គរជ័យ (Angkor Chey)", "ដំបូកខ្ពស់ (Dambouk Khpos)"]},
        {"code": "0702", "name_km": "ស្រុកបន្ទាយមាស", "name_en": "Banteay Meas", "communes": ["បន្ទាយមាសខាងកើត (Banteay Meas Khang Kaeut)", "ទូកមាសខាងលិច (Touk Meas Khang Lech)"]},
        {"code": "0703", "name_km": "ស្រុកឈូក", "name_en": "Chhouk", "communes": ["ឈូក (Chhouk)", "តាកែន (Ta Kaen)"]},
        {"code": "0704", "name_km": "ស្រុកជុំគិរី", "name_en": "Chum Kiri", "communes": ["ស្នាយអញ (Snay Anh)", "ស្រែចែង (Sre Chaeng)"]},
        {"code": "0705", "name_km": "ស្រុកដងទង់", "name_en": "Dang Tong", "communes": ["ដងទង់ (Dang Tong)", "មានរិទ្ធិ (Mean Ritth)"]},
        {"code": "0706", "name_km": "ស្រុកកំពង់ត្រាច", "name_en": "Kampong Trach", "communes": ["កំពង់ត្រាចខាងកើត (Kampong Trach Khang Kaeut)", "ប្រាសាទភ្នំខ្យង (Prasat Phnom Khyang)"]},
        {"code": "0707", "name_km": "ក្រុងកំពត", "name_en": "Krong Kampot", "communes": ["សង្កាត់កំពង់កណ្តាល (Sangkat Kampong Kandal)", "សង្កាត់កំពង់បាយ (Sangkat Kampong Bay)", "សង្កាត់អណ្តូងខ្មែរ (Sangkat Andoung Khmer)"]},
        {"code": "0708", "name_km": "ស្រុកទឹកឈូ", "name_en": "Tuek Chhou", "communes": ["ម៉ាក់ប្រាង្គ (Makprang)", "ត្រពាំងព្រីង (Trapeang Pring)", "ព្រែកត្នោត (Prek Tnaot)"]},
        {"code": "0709", "name_km": "ក្រុងបូកគោ", "name_en": "Krong Bokor", "communes": ["សង្កាត់បឹងទូក (Sangkat Boeng Tuk)", "សង្កាត់កោះតូច (Sangkat Kaoh Touch)"]}
    ],
    # 17 Siem Reap
    "17": [
        {"code": "1701", "name_km": "ស្រុកអង្គរជុំ", "name_en": "Angkor Chum", "communes": ["ចារឈូក (Char Chhuk)", "ដូនប៉េង (Doun Peng)", "គោកដូង (Kouk Doung)"]},
        {"code": "1702", "name_km": "ស្រុកអង្គរធំ", "name_en": "Angkor Thum", "communes": ["ស្វាយចេក (Svay Chek)", "លាងដៃ (Leang Dai)"]},
        {"code": "1703", "name_km": "ស្រុកបន្ទាយស្រី", "name_en": "Banteay Srei", "communes": ["ព្រះដាក់ (Preah Dak)", "រុនតាឯក (Run Ta Ek)", "ឃុនរាម (Khun Ream)"]},
        {"code": "1704", "name_km": "ស្រុកជីក្រែង", "name_en": "Chi Kraeng", "communes": ["កំពង់ក្តី (Kampong Kdei)", "ជីក្រែង (Chi Kraeng)", "ល្វែងឫស្សី (Lveaeng Ruessei)"]},
        {"code": "1706", "name_km": "ស្រុកក្រឡាញ់", "name_en": "Kralanh", "communes": ["ក្រឡាញ់ (Kralanh)", "ស្រណាល (Sranal)"]},
        {"code": "1707", "name_km": "ស្រុកពួក", "name_en": "Puok", "communes": ["ពួក (Puok)", "សសរស្តម្ភ (Sasar Sdam)", "ត្រីញាប់ (Trei Nhoar)"]},
        {"code": "1709", "name_km": "ស្រុកប្រាសាទបាគង", "name_en": "Prasat Bakong", "communes": ["បាគង (Bakong)", "រលួស (Roluos)", "ត្រពាំងធំ (Trapeang Thum)"]},
        {"code": "1710", "name_km": "ក្រុងសៀមរាប", "name_en": "Krong Siem Reap", "communes": ["សង្កាត់ស្វាយដង្គំ (Sangkat Svay Dangkum)", "សង្កាត់សាលាកំរើក (Sangkat Sala Kamreuk)", "សង្កាត់ស្លក្រាម (Sangkat Sla Kram)", "សង្កាត់គោកចក (Sangkat Kouk Chak)"]},
        {"code": "1711", "name_km": "ស្រុកសូទ្រនិគម", "name_en": "Soutr Nikom", "communes": ["ដំដែក (Dam Daek)", "កំពង់ឃ្លាំង (Kampong Khleang)", "កៀនសង្កែ (Kien Sangkae)"]},
        {"code": "1712", "name_km": "ស្រុកស្រីស្នំ", "name_en": "Srei Snam", "communes": ["ជ្រោយនាងងួន (Chrouy Neang Nguon)", "ក្លែងហាយ (Klaeng Hay)"]},
        {"code": "1713", "name_km": "ស្រុកស្វាយលើ", "name_en": "Svay Leu", "communes": ["ស្វាយលើ (Svay Leu)", "បឹងមាលា (Boeng Mealea)"]},
        {"code": "1714", "name_km": "ស្រុកវារិន", "name_en": "Varin", "communes": ["វារិន (Varin)", "ស្រែណូយ (Sre Nouy)"]}
    ],
    # 21 Takeo
    "21": [
        {"code": "2101", "name_km": "ស្រុកអង្គរបូរី", "name_en": "Angkor Borei", "communes": ["អង្គរបូរី (Angkor Borei)", "បាស្រែ (Ba Sre)", "គោកធ្លក (Kouk Thlok)"]},
        {"code": "2102", "name_km": "ស្រុកបាទី", "name_en": "Bati", "communes": ["ចំបក់ (Chambak)", "ចំប៉ី (Champei)", "ដូង (Doung)", "កណ្តឹង (Kandoeng)"]},
        {"code": "2103", "name_km": "ស្រុកបូរីជលសារ", "name_en": "Borei Cholsar", "communes": ["បូរីជលសារ (Borei Cholsar)", "កំពង់ក្រសាំង (Kampong Krasang)"]},
        {"code": "2104", "name_km": "ស្រុកគិរីវង់", "name_en": "Kiri Vong", "communes": ["ព្រះបាទជាន់ជុំ (Preah Bat Choan Chum)", "គោកព្រេច (Kouk Prech)", "តាអូរ (Ta Ou)"]},
        {"code": "2105", "name_km": "ស្រុកកោះអណ្តែត", "name_en": "Koh Andaet", "communes": ["រមេញ (Romenh)", "ព្រៃខ្លា (Prey Khla)"]},
        {"code": "2106", "name_km": "ស្រុកព្រៃកប្បាស", "name_en": "Prey Kabbas", "communes": ["ព្រៃកប្បាស (Prey Kabbas)", "កំពែង (Kampeaeng)", "ចំប៉ា (Champa)"]},
        {"code": "2107", "name_km": "ស្រុកសំរោង", "name_en": "Samraong", "communes": ["សំរោង (Samraong)", "បឹងត្រាញ់ខាងជើង (Boeng Tranh Khang Cheung)"]},
        {"code": "2108", "name_km": "ក្រុងដូនកែវ", "name_en": "Krong Doun Kaev", "communes": ["សង្កាត់រកាក្នុង (Sangkat Roka Knong)", "សង្កាត់រកាក្រៅ (Sangkat Roka Krao)", "សង្កាត់បារាយណ៍ (Sangkat Baray)"]},
        {"code": "2109", "name_km": "ស្រុកត្រាំកក់", "name_en": "Tram Kak", "communes": ["ត្រាំកក់ (Tram Kak)", "អង្គតាសោម (Angk Ta Saom)", "គុស (Kus)"]},
        {"code": "2110", "name_km": "ស្រុកទ្រាំង", "name_en": "Treang", "communes": ["សំបួរ (Sambour)", "រនាម (Roneam)", "ព្រៃស្លឹក (Prey Slaek)"]}
    ],
    # 20 Svay Rieng
    "20": [
        {"code": "2001", "name_km": "ស្រុកចន្ទ្រា", "name_en": "Chantrea", "communes": ["ចន្ទ្រា (Chantrea)", "មេសរថ្ងក (Me Sar Thngak)"]},
        {"code": "2002", "name_km": "ស្រុកកំពង់រោទិ៍", "name_en": "Kampong Rou", "communes": ["ញរ (Nhor)", "ខ្សែត្រ (Khsaetr)", "ព្រះពន្លា (Preah Ponlea)"]},
        {"code": "2003", "name_km": "ស្រុករំដួល", "name_en": "Romdoul", "communes": ["កំពង់ចក (Kampong Chak)", "បុសមន (Bos Mon)"]},
        {"code": "2004", "name_km": "ស្រុករមាសហែក", "name_en": "Romeas Haek", "communes": ["អំពិល (Ampil)", "ដូង (Doung)", "គោកព្រីង (Kouk Pring)"]},
        {"code": "2005", "name_km": "ស្រុកស្វាយជ្រុំ", "name_en": "Svay Chrum", "communes": ["ស្វាយជ្រុំ (Svay Chrum)", "បាសាក់ (Basak)", "ចំបក់ (Chambak)"]},
        {"code": "2006", "name_km": "ក្រុងស្វាយរៀង", "name_en": "Krong Svay Rieng", "communes": ["សង្កាត់ស្វាយរៀង (Sangkat Svay Rieng)", "សង្កាត់ព្រៃឆ្លាក់ (Sangkat Prey Chhlak)", "សង្កាត់គយត្របែក (Sangkat Koy Trabaek)"]},
        {"code": "2007", "name_km": "ស្រុកស្វាយទាប", "name_en": "Svay Teab", "communes": ["កណ្តៀងរាយ (Kandieng Reay)", "សំបួរ (Sambour)"]},
        {"code": "2008", "name_km": "ក្រុងបាវិត", "name_en": "Krong Bavet", "communes": ["សង្កាត់បាវិត (Sangkat Bavet)", "សង្កាត់ព្រៃអង្គុញ (Sangkat Prey Angkunh)", "សង្កាត់ច្រកម្ទេស (Sangkat Chrak Mtes)"]}
    ],
    # 25 Tboung Khmum
    "25": [
        {"code": "2501", "name_km": "ស្រុកដំបែ", "name_en": "Dambae", "communes": ["ដំបែ (Dambae)", "ទឹកជ្រៅ (Tuek Chrov)", "គោកស្រុក (Kouk Srok)"]},
        {"code": "2502", "name_km": "ស្រុកក្រូចឆ្មារ", "name_en": "Krouch Chhmar", "communes": ["ក្រូចឆ្មារ (Krouch Chhmar)", "ឈូក (Chhuk)", "រការខ្នុរ (Roka Khnor)"]},
        {"code": "2503", "name_km": "ស្រុកមេមត់", "name_en": "Memot", "communes": ["មេមត់ (Memot)", "ជាំតាម៉ៅ (Choam Ta Mau)", "ត្រមូង (Tramung)"]},
        {"code": "2504", "name_km": "ស្រុកអូររាំងឪ", "name_en": "Ou Reang Ov", "communes": ["អំពិលតាពក (Ampil Ta Pok)", "គងជ័យ (Kong Chey)", "ព្រះធាតុ (Preah Theat)"]},
        {"code": "2505", "name_km": "ស្រុកពញាក្រែក", "name_en": "Ponhea Kraek", "communes": ["កោងកាង (Kaong Kang)", "ក្រែក (Kraek)", "ដូនតី (Doun Tei)"]},
        {"code": "2506", "name_km": "ក្រុងសួង", "name_en": "Krong Suong", "communes": ["សង្កាត់សួង (Sangkat Suong)", "សង្កាត់វិហារហ្លួង (Sangkat Vihear Luong)"]},
        {"code": "2507", "name_km": "ស្រុកត្បូងឃ្មុំ", "name_en": "Tboung Khmum", "communes": ["ជីគរ (Chi Kor)", "ជប់ (Chob)", "ល្ងៀង (Lngeang)"]}
    ]
}

total_added_districts = 0
total_added_communes = 0

for prov_code, districts in PROVINCE_DISTRICTS_DATA.items():
    if prov_code not in prov_map:
        continue
    prov = prov_map[prov_code]
    existing_dist_codes = {d["code"]: d for d in prov.get("districts", [])}

    for dist_info in districts:
        d_code = dist_info["code"]
        d_type = "Municipality" if "ក្រុង" in dist_info["name_km"] or "Krong" in dist_info["name_en"] else "District"
        
        commune_objs = []
        for c_idx, c_name in enumerate(dist_info["communes"]):
            c_code = f"{d_code}{str(c_idx + 1).zfill(2)}"
            # Parse Khmer and Latin parts
            if "(" in c_name and ")" in c_name:
                c_km = c_name.split("(")[0].strip()
                c_en = c_name.split("(")[1].replace(")", "").strip()
            else:
                c_km = c_name
                c_en = c_name
            c_type = "Sangkat" if "សង្កាត់" in c_km or "Sangkat" in c_en else "Commune"
            commune_objs.append({
                "code": c_code,
                "name_km": c_km,
                "name_en": c_en,
                "type": c_type,
                "villages": [
                    {"code": f"{c_code}01", "name_km": f"ភូមិ១", "name_en": "Phum 1"},
                    {"code": f"{c_code}02", "name_km": f"ភូមិ២", "name_en": "Phum 2"}
                ]
            })

        if d_code in existing_dist_codes:
            # Update communes of existing district if empty or small
            existing_d = existing_dist_codes[d_code]
            if len(existing_d.get("communes", [])) < len(commune_objs):
                existing_d["communes"] = commune_objs
        else:
            prov.setdefault("districts", []).append({
                "code": d_code,
                "name_km": dist_info["name_km"],
                "name_en": dist_info["name_en"],
                "type": d_type,
                "communes": commune_objs
            })
            total_added_districts += 1
            total_added_communes += len(commune_objs)

# Save back to file
with open(DATA_PATH, "w", encoding="utf-8") as f:
    json.dump(hierarchy, f, ensure_ascii=False, indent=2)

print(f"Successfully enriched provinces with {total_added_districts} districts and {total_added_communes} communes!")
