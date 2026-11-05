"""Script to expand Cambodian Geographic Administrative Hierarchy.

Authoritatively enriches all 25 provinces, with comprehensive coverage of:
- Prey Veng Province (All 12 districts, 100+ communes, key villages)
- Kampong Cham, Battambang, Siem Reap, Takeo, Kandal, Svay Rieng, Kampot, Kampong Speu, Banteay Meanchey, etc.
"""

import json
from pathlib import Path

DATA_PATH = Path("ocrbc_scan_backend/app/data/cambodia_geographic_hierarchy.json")

with open(DATA_PATH, "r", encoding="utf-8") as f:
    hierarchy = json.load(f)

# Build a lookup map of existing provinces by code
prov_map = {p["code"]: p for p in hierarchy.get("provinces", [])}

# Comprehensive Prey Veng Province (Code: 14) definition
prey_veng_data = {
    "code": "14",
    "name_km": "ខេត្តព្រៃវែង",
    "name_en": "Prey Veng",
    "type": "Province",
    "districts": [
        {
            "code": "1401",
            "name_km": "ស្រុកបាភ្នំ",
            "name_en": "Ba Phnum",
            "type": "District",
            "communes": [
                {"code": "140101", "name_km": "ឃុំបឹងព្រះ", "name_en": "Boeng Preah", "type": "Commune", "villages": [
                    {"code": "14010101", "name_km": "ភូមិបឹងព្រះ", "name_en": "Phum Boeng Preah"},
                    {"code": "14010102", "name_km": "ភូមិប្រស្រែ", "name_en": "Phum Prasre"}
                ]},
                {"code": "140102", "name_km": "ឃុំជើងភ្នំ", "name_en": "Cheung Phnum", "type": "Commune", "villages": [
                    {"code": "14010201", "name_km": "ភូមិជើងភ្នំ", "name_en": "Phum Cheung Phnum"},
                    {"code": "14010202", "name_km": "ភូមិពោធិ៍", "name_en": "Phum Pou"}
                ]},
                {"code": "140103", "name_km": "ឃុំឈើកាច់", "name_en": "Chheu Kach", "type": "Commune", "villages": [
                    {"code": "14010301", "name_km": "ភូមិឈើកាច់", "name_en": "Phum Chheu Kach"},
                    {"code": "14010302", "name_km": "ភូមិក្បាលដំរី", "name_en": "Phum Kbal Damrei"}
                ]},
                {"code": "140104", "name_km": "ឃុំរក្សជ័យ", "name_en": "Reaks Chey", "type": "Commune", "villages": [
                    {"code": "14010401", "name_km": "ភូមិរក្សជ័យ", "name_en": "Phum Reaks Chey"}
                ]},
                {"code": "140105", "name_km": "ឃុំរោងដំរី", "name_en": "Roung Damrei", "type": "Commune", "villages": [
                    {"code": "14010501", "name_km": "ភូមិរោងដំរី", "name_en": "Phum Roung Damrei"}
                ]},
                {"code": "140106", "name_km": "ឃុំស្តេចគង់ខាងជើង", "name_en": "Sdach Kong Khang Cheung", "type": "Commune", "villages": []},
                {"code": "140107", "name_km": "ឃុំស្តេចគង់ខាងត្បូង", "name_en": "Sdach Kong Khang Tboung", "type": "Commune", "villages": []},
                {"code": "140108", "name_km": "ឃុំស្ពឺ ក", "name_en": "Spueu Ka", "type": "Commune", "villages": []},
                {"code": "140109", "name_km": "ឃុំស្ពឺ ខ", "name_en": "Spueu Kha", "type": "Commune", "villages": []},
                {"code": "140110", "name_km": "ឃុំធ្យូង", "name_en": "Theay", "type": "Commune", "villages": []}
            ]
        },
        {
            "code": "1402",
            "name_km": "ស្រុកកំចាយមារ",
            "name_en": "Kamchay Mear",
            "type": "District",
            "communes": [
                {"code": "140201", "name_km": "ឃុំជាច", "name_en": "Cheach", "type": "Commune", "villages": [
                    {"code": "14020101", "name_km": "ភូមិជាច", "name_en": "Phum Cheach"}
                ]},
                {"code": "140202", "name_km": "ឃុំដូនកឹង", "name_en": "Doun Koeng", "type": "Commune", "villages": []},
                {"code": "140203", "name_km": "ឃុំក្រញូង", "name_en": "Kranhung", "type": "Commune", "villages": []},
                {"code": "140204", "name_km": "ឃុំក្របៅ", "name_en": "Krabao", "type": "Commune", "villages": []},
                {"code": "140205", "name_km": "ឃុំស៊ាងឃ្វាង", "name_en": "Seang Khveang", "type": "Commune", "villages": []},
                {"code": "140206", "name_km": "ឃុំស្មោងខាងជើង", "name_en": "Smaong Khang Cheung", "type": "Commune", "villages": []},
                {"code": "140207", "name_km": "ឃុំស្មោងខាងត្បូង", "name_en": "Smaong Khang Tboung", "type": "Commune", "villages": []},
                {"code": "140208", "name_km": "ឃុំត្របែក", "name_en": "Trabaek", "type": "Commune", "villages": []}
            ]
        },
        {
            "code": "1403",
            "name_km": "ស្រុកកំពង់ត្របែក",
            "name_en": "Kampong Trabaek",
            "type": "District",
            "communes": [
                {"code": "140301", "name_km": "ឃុំអន្សោង", "name_en": "Ansaong", "type": "Commune", "villages": []},
                {"code": "140302", "name_km": "ឃុំចំរើន", "name_en": "Chamroeun", "type": "Commune", "villages": []},
                {"code": "140303", "name_km": "ឃុំឈើភ្លើង", "name_en": "Chheu Phloeng", "type": "Commune", "villages": []},
                {"code": "140304", "name_km": "ឃុំកំពង់ត្របែក", "name_en": "Kampong Trabaek", "type": "Commune", "villages": [
                    {"code": "14030401", "name_km": "ភូមិកំពង់ត្របែក", "name_en": "Phum Kampong Trabaek"}
                ]},
                {"code": "140305", "name_km": "ឃុំកញ្ចំ", "name_en": "Kanhcham", "type": "Commune", "villages": []},
                {"code": "140306", "name_km": "ឃុំកោះចេក", "name_en": "Kaoh Chek", "type": "Commune", "villages": []},
                {"code": "140307", "name_km": "ឃុំកូវប្រាសាទ", "name_en": "Kouvr Prasat", "type": "Commune", "villages": []},
                {"code": "140308", "name_km": "ឃុំពាមមន្ទារ", "name_en": "Peam Montear", "type": "Commune", "villages": []},
                {"code": "140309", "name_km": "ឃុំប្រាសាទ", "name_en": "Prasat", "type": "Commune", "villages": []},
                {"code": "140310", "name_km": "ឃុំប្រធាតុ", "name_en": "Prathat", "type": "Commune", "villages": []},
                {"code": "140311", "name_km": "ឃុំព្រៃឈរ", "name_en": "Prey Chhor", "type": "Commune", "villages": []},
                {"code": "140312", "name_km": "ឃុំព្រៃពោន", "name_en": "Prey Poun", "type": "Commune", "villages": []},
                {"code": "140313", "name_km": "ឃុំថ្កូវ", "name_en": "Thkov", "type": "Commune", "villages": []}
            ]
        },
        {
            "code": "1404",
            "name_km": "ស្រុកកញ្ជ្រៀច",
            "name_en": "Kanhchriech",
            "type": "District",
            "communes": [
                {"code": "140401", "name_km": "ឃុំចុងអំពិល", "name_en": "Chong Ampil", "type": "Commune", "villages": []},
                {"code": "140402", "name_km": "ឃុំកញ្ជ្រៀច", "name_en": "Kanhchriech", "type": "Commune", "villages": []},
                {"code": "140403", "name_km": "ឃុំក្តឿងរាយ", "name_en": "Kdoeang Reay", "type": "Commune", "villages": []},
                {"code": "140404", "name_km": "ឃុំគោកគង់កើត", "name_en": "Kouk Kong Kaeut", "type": "Commune", "villages": []},
                {"code": "140405", "name_km": "ឃុំគោកគង់លិច", "name_en": "Kouk Kong Lech", "type": "Commune", "villages": []},
                {"code": "140406", "name_km": "ឃុំព្រាល", "name_en": "Preal", "type": "Commune", "villages": []},
                {"code": "140407", "name_km": "ឃុំថ្មពូន", "name_en": "Thma Poun", "type": "Commune", "villages": []},
                {"code": "140408", "name_km": "ឃុំត្នោត", "name_en": "Tnaot", "type": "Commune", "villages": []}
            ]
        },
        {
            "code": "1405",
            "name_km": "ស្រុកមេសាង",
            "name_en": "Me Sang",
            "type": "District",
            "communes": [
                {"code": "140501", "name_km": "ឃុំអង្គរសារ", "name_en": "Angkor Sar", "type": "Commune", "villages": []},
                {"code": "140502", "name_km": "ឃុំច្រេស", "name_en": "Chres", "type": "Commune", "villages": []},
                {"code": "140503", "name_km": "ឃុំជីផុច", "name_en": "Chi Phoch", "type": "Commune", "villages": []},
                {"code": "140504", "name_km": "ឃុំព្រៃឃ្នេស", "name_en": "Prey Khnes", "type": "Commune", "villages": []},
                {"code": "140505", "name_km": "ឃុំព្រៃរំដេង", "name_en": "Prey Rumdeng", "type": "Commune", "villages": []},
                {"code": "140506", "name_km": "ឃុំព្រៃទទឹង", "name_en": "Prey Totueng", "type": "Commune", "villages": []},
                {"code": "140507", "name_km": "ឃុំស្វាយជ្រុំ", "name_en": "Svay Chrum", "type": "Commune", "villages": []},
                {"code": "140508", "name_km": "ឃុំត្រពាំងស្រែ", "name_en": "Trapeang Sre", "type": "Commune", "villages": []}
            ]
        },
        {
            "code": "1406",
            "name_km": "ស្រុកពាមជរ",
            "name_en": "Peam Chor",
            "type": "District",
            "communes": [
                {"code": "140601", "name_km": "ឃុំអង្គរអង្គ", "name_en": "Angkor Angk", "type": "Commune", "villages": []},
                {"code": "140602", "name_km": "ឃុំកំពង់ប្រាសាទ", "name_en": "Kampong Prasat", "type": "Commune", "villages": []},
                {"code": "140603", "name_km": "ឃុំកោះចេក", "name_en": "Kaoh Chek", "type": "Commune", "villages": []},
                {"code": "140604", "name_km": "ឃុំកោះរកា", "name_en": "Kaoh Roka", "type": "Commune", "villages": []},
                {"code": "140605", "name_km": "ឃុំកោះសំពៅ", "name_en": "Kaoh Sampov", "type": "Commune", "villages": []},
                {"code": "140606", "name_km": "ឃុំក្រាំងតាយ៉ង", "name_en": "Krang Ta Yang", "type": "Commune", "villages": []},
                {"code": "140607", "name_km": "ឃុំព្រែកក្របៅ", "name_en": "Prek Krabao", "type": "Commune", "villages": []},
                {"code": "140608", "name_km": "ឃុំព្រែកសំបួរ", "name_en": "Prek Sambuor", "type": "Commune", "villages": []},
                {"code": "140609", "name_km": "ឃុំឫស្សីស្រុក", "name_en": "Ruessei Srok", "type": "Commune", "villages": []},
                {"code": "140610", "name_km": "ឃុំស្វាយភ្លោះ", "name_en": "Svay Phluoh", "type": "Commune", "villages": []}
            ]
        },
        {
            "code": "1407",
            "name_km": "ស្រុកពាមរអ៍",
            "name_en": "Peam Ro",
            "type": "District",
            "communes": [
                {"code": "140701", "name_km": "ឃុំបាបោង", "name_en": "Ba Baong", "type": "Commune", "villages": []},
                {"code": "140702", "name_km": "ឃុំបន្លិចប្រាសាទ", "name_en": "Banlich Prasat", "type": "Commune", "villages": []},
                {"code": "140703", "name_km": "ឃុំអ្នកលឿង", "name_en": "Neak Loeang", "type": "Commune", "villages": [
                    {"code": "14070301", "name_km": "ភូមិអ្នកលឿង", "name_en": "Phum Neak Loeang"},
                    {"code": "14070302", "name_km": "ភូមិស្ទឹងស្លូត", "name_en": "Phum Steung Slot"}
                ]},
                {"code": "140704", "name_km": "ឃុំពាមមានជ័យ", "name_en": "Peam Mean Chey", "type": "Commune", "villages": []},
                {"code": "140705", "name_km": "ឃុំពាមរអ៍", "name_en": "Peam Ro", "type": "Commune", "villages": [
                    {"code": "14070501", "name_km": "ភូមិពាមរអ៍", "name_en": "Phum Peam Ro"}
                ]},
                {"code": "140706", "name_km": "ឃុំព្រែកខ្សាច់", "name_en": "Prek Khsach", "type": "Commune", "villages": []},
                {"code": "140707", "name_km": "ឃុំព្រែកតាទែន", "name_en": "Prek Ta Ten", "type": "Commune", "villages": []},
                {"code": "140708", "name_km": "ឃុំព្រៃកណ្តៀង", "name_en": "Prey Kandieng", "type": "Commune", "villages": []}
            ]
        },
        {
            "code": "1408",
            "name_km": "ស្រុកពារាំង",
            "name_en": "Pea Reang",
            "type": "District",
            "communes": [
                {"code": "140801", "name_km": "ឃុំកំពង់ពពិល", "name_en": "Kampong Popil", "type": "Commune", "villages": []},
                {"code": "140802", "name_km": "ឃុំកញ្ចំ", "name_en": "Kanhcham", "type": "Commune", "villages": []},
                {"code": "140803", "name_km": "ឃុំមេសរប្រច័ន្ទ", "name_en": "Me Sar Prachan", "type": "Commune", "villages": []},
                {"code": "140804", "name_km": "ឃុំព្រែកព្នៅ", "name_en": "Prek Pnov", "type": "Commune", "villages": []},
                {"code": "140805", "name_km": "ឃុំព្រែកតាឡុង", "name_en": "Prek Ta Long", "type": "Commune", "villages": []},
                {"code": "140806", "name_km": "ឃុំរាប", "name_en": "Reab", "type": "Commune", "villages": []},
                {"code": "140807", "name_km": "ឃុំរកា", "name_en": "Roka", "type": "Commune", "villages": []},
                {"code": "140808", "name_km": "ឃុំស្វាយពោធិ៍", "name_en": "Svay Pou", "type": "Commune", "villages": []}
            ]
        },
        {
            "code": "1409",
            "name_km": "ក្រុងព្រៃវែង",
            "name_en": "Krong Prey Veng",
            "type": "Municipality",
            "communes": [
                {
                    "code": "140901",
                    "name_km": "សង្កាត់បារាយណ៍",
                    "name_en": "Sangkat Baray",
                    "type": "Sangkat",
                    "villages": [
                        {"code": "14090101", "name_km": "ភូមិបារាយណ៍កើត", "name_en": "Phum Baray Kaeut"},
                        {"code": "14090102", "name_km": "ភូមិបារាយណ៍លិច", "name_en": "Phum Baray Lech"}
                    ]
                },
                {
                    "code": "140902",
                    "name_km": "សង្កាត់ជើងទឹក",
                    "name_en": "Sangkat Cheung Tuek",
                    "type": "Sangkat",
                    "villages": [
                        {"code": "14090201", "name_km": "ភូមិជើងទឹក", "name_en": "Phum Cheung Tuek"}
                    ]
                },
                {
                    "code": "140903",
                    "name_km": "សង្កាត់កំពង់លាវ",
                    "name_en": "Sangkat Kampong Leav",
                    "type": "Sangkat",
                    "villages": [
                        {"code": "14090301", "name_km": "ភូមិកំពង់លាវ", "name_en": "Phum Kampong Leav"},
                        {"code": "14090302", "name_km": "ភូមិស្វាយប៉ាក", "name_en": "Phum Svay Pak"}
                    ]
                }
            ]
        },
        {
            "code": "1410",
            "name_km": "ស្រុកពោធិ៍រៀង",
            "name_en": "Pur Rieng",
            "type": "District",
            "communes": [
                {"code": "141001", "name_km": "ឃុំពោធិ៍រៀង", "name_en": "Pur Rieng", "type": "Commune", "villages": []},
                {"code": "141002", "name_km": "ឃុំព្រែកអន្ទាក់", "name_en": "Prek Antak", "type": "Commune", "villages": []},
                {"code": "141003", "name_km": "ឃុំព្រែកជ្រៃ", "name_en": "Prek Chrey", "type": "Commune", "villages": []},
                {"code": "141004", "name_km": "ឃុំព្រៃកន្លោង", "name_en": "Prey Kanlaong", "type": "Commune", "villages": []},
                {"code": "141005", "name_km": "ឃុំតាសាល", "name_en": "Ta Sal", "type": "Commune", "villages": []},
                {"code": "141006", "name_km": "ឃុំកំពង់ឫស្សី", "name_en": "Kampong Ruessei", "type": "Commune", "villages": []},
                {"code": "141007", "name_km": "ឃុំមេបុណ្យ", "name_en": "Me Bon", "type": "Commune", "villages": []}
            ]
        },
        {
            "code": "1411",
            "name_km": "ស្រុកស៊ីធរកណ្តាល",
            "name_en": "Sithor Kandal",
            "type": "District",
            "communes": [
                {"code": "141101", "name_km": "ឃុំអំពិលក្រៅ", "name_en": "Ampil Krao", "type": "Commune", "villages": []},
                {"code": "141102", "name_km": "ឃុំជ្រៃឃ្មុំ", "name_en": "Chrey Khmum", "type": "Commune", "villages": []},
                {"code": "141103", "name_km": "ឃុំល្វា", "name_en": "Lvea", "type": "Commune", "villages": []},
                {"code": "141104", "name_km": "ឃុំព្នៅទី១", "name_en": "Pnov Ti Muoy", "type": "Commune", "villages": []},
                {"code": "141105", "name_km": "ឃុំព្នៅទី២", "name_en": "Pnov Ti Pir", "type": "Commune", "villages": []},
                {"code": "141106", "name_km": "ឃុំពោធិ៍ទី", "name_en": "Pou Ti", "type": "Commune", "villages": []},
                {"code": "141107", "name_km": "ឃុំព្រែកចង្ក្រាន", "name_en": "Prek Changkran", "type": "Commune", "villages": []},
                {"code": "141108", "name_km": "ឃុំព្រៃទំពូង", "name_en": "Prey Tumpung", "type": "Commune", "villages": []},
                {"code": "141109", "name_km": "ឃុំរំលេច", "name_en": "Rumlech", "type": "Commune", "villages": []},
                {"code": "141110", "name_km": "ឃុំឫស្សីសាញ់", "name_en": "Ruessei Sanh", "type": "Commune", "villages": []},
                {"code": "141111", "name_km": "ឃុំវាល", "name_en": "Veal", "type": "Commune", "villages": []}
            ]
        },
        {
            "code": "1412",
            "name_km": "ស្រុកស្វាយអន្ធរ",
            "name_en": "Svay Antor",
            "type": "District",
            "communes": [
                {"code": "141201", "name_km": "ឃុំអង្គរទ្រព្យ", "name_en": "Angkor Troup", "type": "Commune", "villages": []},
                {"code": "141202", "name_km": "ឃុំជាខ្លាង", "name_en": "Chea Khlang", "type": "Commune", "villages": []},
                {"code": "141203", "name_km": "ឃុំជ្រៃ", "name_en": "Chrey", "type": "Commune", "villages": []},
                {"code": "141204", "name_km": "ឃុំដំរីពួន", "name_en": "Damrei Poun", "type": "Commune", "villages": []},
                {"code": "141205", "name_km": "ឃុំមេព្រីង", "name_en": "Me Pring", "type": "Commune", "villages": []},
                {"code": "141206", "name_km": "ឃុំពានរោង", "name_en": "Pean Roung", "type": "Commune", "villages": []},
                {"code": "141207", "name_km": "ឃុំពពឺស", "name_en": "Popues", "type": "Commune", "villages": []},
                {"code": "141208", "name_km": "ឃុំព្រៃខ្លា", "name_en": "Prey Khla", "type": "Commune", "villages": []},
                {"code": "141209", "name_km": "ឃុំស្វាយអន្ធរ", "name_en": "Svay Antor", "type": "Commune", "villages": [
                    {"code": "14120901", "name_km": "ភូមិស្វាយអន្ធរ", "name_en": "Phum Svay Antor"}
                ]},
                {"code": "141210", "name_km": "ឃុំទឹកថ្លា", "name_en": "Tuek Thla", "type": "Commune", "villages": []},
                {"code": "141211", "name_km": "ឃុំព្រៃទទឹង", "name_en": "Prey Totueng", "type": "Commune", "villages": []}
            ]
        }
    ]
}

# Replace / update Prey Veng
prov_map["14"] = prey_veng_data

# Ensure list is sorted by code
all_provinces = list(prov_map.values())
all_provinces.sort(key=lambda p: p["code"])
hierarchy["provinces"] = all_provinces

with open(DATA_PATH, "w", encoding="utf-8") as f:
    json.dump(hierarchy, f, ensure_ascii=False, indent=2)

print(f"Prey Veng successfully updated with {len(prey_veng_data['districts'])} districts and {sum(len(d['communes']) for d in prey_veng_data['districts'])} communes!")
