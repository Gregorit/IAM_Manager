# Praca magisterska : Tworzenie systemu kotroli uprawnień
Idea działania. System ma dwa tryby pracy. Pełnego audytu , gdzie rola/user ma pełne uprawnienia, oraz trybu pracy, gdzie działą z już uzyskanymi upranieniami

    - wykrywanie anomalii na podstawie CloudTrail / VPC Flow Log
    - budowanie zachowań użytkownika i wykrywanie anomalii
    - stopniowanie anomalii
    - stosowne zachowanie się w danych anomaliach - przykłady:
        * powiadomienie z użyciem SNS
        * odcięcie użytkownika od dostępu do części środowiska
        * redukcja uprawnień na koncie AWS
Fin,
