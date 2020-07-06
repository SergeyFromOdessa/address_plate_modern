pip install reportlab

files
    address_plate.py
    paths.pkl

commands example:

python3 address_plate.py --wide vertical --street_type "улица" --street_name "street name" --street_translit translit --house_num "25/3А" > test1.pdf
python3 address_plate.py name --street_type "проспект" --street_name "Название Проспекта" --street_translit translit > test2.pdf
python3 address_plate.py number --house_num "25/3А" --left_num 23А > test3.pdf

python3 address_plate.py vertical --street_type "вулиця" --street_name "Омеляновича-Павленка" --street_translit "Omelyanovycha-Pavlenka vulytsia" --house_num "25" > Омеляновича-Павленка25.pdf
python3 address_plate.py vertical --street_type "вулиця" --street_name "Іоанна Павла ІІ" --street_translit "Ioanna Pavla Druhoho vulytsia" --house_num "5/4А" > Іоанна_Павла_ІІ_5_4А.pdf
python3 address_plate.py name --street_type "вулиця" --street_name "Хорива" --street_translit "Khoryva vulytsia" > Хорива.pdf
python3 address_plate.py number --house_num "12" --left_num 14 --right_num 12А > 12-14-12A.pdf


