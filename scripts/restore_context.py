"""Brief conditional impact scenarios derived from the reported topic."""
import re

RULES = [
    (r'špion|špión', 'Pokud se podezření potvrdí, může následovat trestní stíhání a přísnější ochrana citlivých technologií či informací. Samotné vyšetřování vinu neprokazuje.'),
    (r'plakát|kauz.*spd|spd.*soud', 'Rozhodnutí soudu může ovlivnit podobu dalších volebních kampaní a to, kde bude hranice mezi politickou kritikou a podněcováním nenávisti.'),
    (r'volb.*neplatn|hlasování.*neplatn|neplatn.*hlasování|volit znovu', 'Opakování hlasování může oddálit vznik vedení obce a změnit rozdělení mandátů. Do vyjasnění výsledku se mohou zdržet některá místní rozhodnutí.'),
    (r'e-žádank|elektronick.*žádank', 'Pokud se povinnost zavede, může pacientům zjednodušit předávání žádanek mezi lékaři. Ordinace ale mohou potřebovat úpravy softwaru a nové pracovní postupy.'),
    (r'kybernet|hacktiv|hacke|kyberš', 'Další útoky mohou narušit služby nebo vést k úniku dat. Pro dotčené instituce to může znamenat náklady na obnovu provozu a posílení zabezpečení.'),
    (r'uměl.*inteligenc|\bai\b|openai', 'Přísnější pravidla mohou zvýšit odpovědnost technologických firem a ochranu uživatelů. Mohou ale také zpomalit zavádění některých služeb a zvýšit náklady na jejich provoz.'),
    (r'průzkum|median|volební model', 'Pokud se trend udrží, může změnit vyjednávací sílu stran a složení možných koalic. Samotný průzkum ale neurčuje výsledek příštích voleb.'),
    (r'unijní rozpočet|rozpočet.*ukrajin', 'Spor může oddálit dohodu o evropském rozpočtu nebo pomoci Ukrajině. Kompromis může ovlivnit, kolik peněz poskytnou jednotlivé státy a za jakých podmínek.'),
    (r'hraniční.*zdi|hranic.*mexik|zdi.*park', 'Pokračování stavby může změnit situaci v příhraničí a zasáhnout chráněná území. Další soudní spory mohou ovlivnit tempo výstavby i její náklady.'),
    (r'pomoc.*izrael|izrael.*pomoc', 'Změna americké podpory může ovlivnit možnosti izraelské vlády i její vyjednávání. Případné podmínky pomoci by mohly zvýšit tlak na změnu jejího postupu.'),
    (r'letoun|leteck.*základ|bombard', 'Přesuny letadel mohou změnit dostupnost vojenské podpory a ochranu základen. Při dalším růstu napětí mohou spojenci upravovat rozmístění sil i bezpečnostní opatření.'),
    (r'ostřelov|ruském útoku|útok.*ukrajinsk|kyjevsk.*čtvrť', 'Další útoky mohou zhoršit bezpečnost civilistů a narušit dopravu, dodávky energie či fungování měst. Mohou také zvýšit potřebu evakuací a humanitární pomoci.'),
    (r'manžel.*okupac|okupac.*rodin', 'Pokračující okupace může dál komplikovat návrat obyvatel a slučování rodin. Pro postižené domácnosti to může znamenat delší nejistotu ohledně bydlení a obživy.'),
    (r'oslab.*rusk|rusk.*sport|hokej|sportovní arbitráž', 'Spor může ovlivnit účast sportovců na mezinárodních soutěžích a vztahy mezi svazy. Diplomatické reakce mohou přenést téma i do jednání mezi státy.'),
    (r'ocenil zachránce|záchranářsk', 'Zviditelnění oceněných může posílit zájem o první pomoc a podporu záchranářů. Přímá změna pravidel nebo financování z ocenění sama nevyplývá.'),
    (r'příměří|mírov|jednání.*ukončení|rozhovory.*ukrajin|jednání.*válk|bezpečnostní rámec', 'Dohoda by mohla omezit boje a otevřít prostor pro bezpečnostní záruky či obnovu země. Pokud jednání selžou, nejistota pro obyvatele i spojence může pokračovat.'),
    (r'zdravot|pojišťovn|nemocnic', 'Změna může ovlivnit dostupnost péče, financování zdravotnictví nebo práci zdravotníků. Rozhodující bude schválená podoba opatření a jeho zavedení do praxe.'),
    (r'energie|energetik|elektřin|plyn', 'Výsledek může ovlivnit jistotu dodávek a náklady na energie pro domácnosti či firmy. Konkrétní dopad závisí na uzavřených dohodách a podmínkách jejich plnění.'),
    (r'rozpoč|daně|důchod|dávk|veřejné finance', 'Přijatá změna může ovlivnit příjmy domácností nebo peníze na veřejné služby. Dokud není schválená její konečná podoba, dopad nelze určit přesně.'),
    (r'zákon|novel|legislativ', 'Pokud se návrh schválí, mohou se změnit práva nebo povinnosti dotčených lidí a institucí. Praktický dopad bude záviset na konečném znění a termínu účinnosti.'),
    (r'volb|voleb|mandát|koalic|starost|zastupitel', 'Vývoj může změnit složení vedení a priority při rozhodování o veřejných penězích. Výsledek bude záviset na dalších jednáních a konkrétních dohodách.'),
    (r'válk|ukrajin|gaza|írán', 'Další vývoj může ovlivnit bezpečnost obyvatel, humanitární situaci i vztahy mezi státy. Zhoršení situace může zvýšit nároky na pomoc a tlak na diplomatická jednání.'),
]

def importance(row):
    title = row['title']
    text = title + ' ' + row.get('summary', '')
    # This combination is specific enough to separate the domestic anniversary
    # dispute from unrelated diplomatic visits mentioned in the same feed.
    if re.search(r'17\.?\s*listopad', text, re.I) and re.search(r'babiš|premiér', text, re.I):
        return 'Neúčast premiéra může zesílit kritiku opozice a přesunout pozornost od oslav k politickému sporu. Dopad na důvěru veřejnosti bude záviset i na dalším vysvětlení vlády.'
    for pattern, impact in RULES:
        if re.search(pattern, text, re.I):
            return impact
    if re.search(r'prezident|premiér|ministr|vlád|diplomat', text, re.I):
        return 'Pokud na vyjádření navážou konkrétní kroky, mohou změnit priority vlády nebo vztahy s jejími partnery. Bez následného rozhodnutí může dopad zůstat hlavně v politické debatě.'
    return ('Další postup může ovlivnit rozhodování příslušných úřadů a lidí, kterých se téma týká. Z dostupného popisu nelze konkrétnější dopad spolehlivě odhadnout.'
            if row['category'] == 'domaci' else
            'Další reakce mohou ovlivnit vztahy mezi zúčastněnými zeměmi nebo institucemi. Z dostupného popisu nelze konkrétnější dopad spolehlivě odhadnout.')
