# Politický přehled

> **Aktuální provoz od 12. 11. 2026:** hodinový sběr a publikaci provádí bez AI GitHub Actions v repozitáři `davhab-dev/davhab-dev.github.io`, workflow `.github/workflows/politicky-prehled.yml` (cron v minutě :12). ChatGPT vytváří pouze rozbory v 06:00 a 18:00 Europe/Prague, nejvýše osm událostí za cyklus; výsledky ukládá do `scripts/impact_notes.json`. Publikují se při dalším hodinovém sběru. Aktuální pokyny jsou v `scripts/EDITORIAL_CYCLE.md`. Starší odstavce README o hodinové AI úloze popisují historický provoz.

Veřejná stránka: https://davhab.com/politicky-prehled/

Tento repozitář je samostatným zdrojem aplikace. Kontroly kódu běží v `.github/workflows/check.yml`. Veřejnou adresu zajišťuje repozitář `davhab-dev/davhab-dev.github.io`. Pravidelný sběr, okamžité zveřejnění článků a následné rozbory řídí jediná hodinová úloha ChatGPT podle postupu níže. GitHub workflow slouží jen k ruční obnově.

`scripts/update_politics.py` načte veřejné RSS/Atom ze seznamu `sources.json` (16 českých redakcí), ponechá jen články vydané za posledních 24 hodin, vybere domácí a zahraniční politiku podle rubriky a výrazů, odstraní stejné URL a podobné titulky a ověří dostupnost odkazů. Nejvýše 20 článků na rubriku a čtyři články jedné redakce v rubrice; počet se nedoplňuje starými zprávami. Anotace jsou označené krátké výňatky (nejvýše 25 slov), nikoli nově vytvořené AI analýzy či nezávislé ověření tvrzení. Výběr podle výrazů může některá témata vynechat či zahrnout nepřesně. Datum vydání článku není automaticky datem popisované události.

Výchozí je aktuální vydání. Archiv obsahuje samostatné neměnné JSON snímky každé úspěšné aktualizace a seznam v `archive/index.json`. Výběr data a času načte tehdejší obsah, který se při dalších aktualizacích nepřepisuje. V archivu se starší články neskrývají podle dnešního data. Časy jsou uvedeny v Praze; archiv obsahuje pouze skutečně uložená vydání. Otevřená stránka kontroluje nové vydání každých 5 minut a průběžně skrývá články starší než 24 hodin. Časy jsou v Europe/Prague. Po více než dvou hodinách bez úspěšné aktualizace zobrazí upozornění. Při výpadku všech zdrojů nebo kontrol článků se poslední vydání ani čas úspěšné aktualizace nepřepisují; částečný výpadek zdrojů je uveden na stránce.

Publikační workflow v repozitáři webu uloží nové HTML a JSON a výslovně požádá o sestavení branch-based GitHub Pages (commit s GITHUB_TOKEN sám sestavení nespouští). Používá pouze oprávnění contents:write a pages:write, bez dalších API klíčů. Nezasahuje do ostatních projektů.

Ověření: `python -m unittest discover -s scripts -p 'test_update_politics.py'`. Ruční obnova: `python scripts/update_politics.py` (Python 3.12+, curl).

Rámeček „Proč je to důležité“ zobrazuje konkrétní rozbor a odkaz na ověřený podklad. Hodinová redakční úloha zpracuje všechny nové články posledního vydání, doplní záznamy do `scripts/impact_notes.json` a promítne je do živých dat a HTML pomocí `python scripts/apply_impact_notes.py cesta/k/politicky-prehled`. Nový článek čeká na ověření s viditelným stavem. Shoda URL a titulku umožňuje použít hotový rozbor i při dalším sběru. Dříve vydané archivní snímky zachovávají původní obsah. Čas poslední kontroly zpráv se při doplnění komentáře nemění.

Rozbalovací Seznam zdrojů používá stejný schválený katalog jako aktualizační skript. Výběr vychází z dohledatelné redakce, redakčních standardů a veřejných podkladů NFNZ (https://www.nfnz.cz/rating-medii/, https://www.nfnz.cz/dezinformacni-a-konspiracni-media/), ověřeno 10. 11. 2026. Nejde o automatický slib pokrytí každého českého webu ani o záruku správnosti všech tvrzení. Nové domény vyžadují výslovné zařazení; přesměrování mimo schválené domény se odmítá.

U smíšených placených/volných webů se vyžaduje pozitivní `isAccessibleForFree` nebo ověřený příznak volného článku konkrétního vydavatele (`locked:false`, `content=free` a `premium=false`); záporný příznak či zjištěná výzva k odemčení vede k vyřazení. Zároveň je vyžadován dostupný text článku. Konzervativní kontrola může vynechat i volný článek bez potřebných metadat. U veřejných zdrojů se vyžaduje dostupný text a nepřítomnost zjištěného uzamčení. Kontrola nenahrazuje ruční čtení či ověření tvrzení.

Z každé redakce se kontroluje nejvýše osm aktuálních politických kandidátů při jednom běhu, poté se odstraňují podobné titulky a uplatňuje pestrost redakcí. Výpadky a počty vybraných článků jsou uloženy v datech vydání a uvedeny v Seznamu zdrojů. České noviny slouží pro titulky a odkazy; jejich anotace se nepřebírají. Běžný informační pruh je odstraněn; případné upozornění na zpoždění nebo výpadek se zobrazí pouze při problému.

## Struktura

- `index.html`, `app.js`, `sources.json`: vzhled, ovládání a schválené redakce.
- `scripts/`: automatické získání zpráv, kontrola přístupu a archivace.
- `data.json`, `archive/`: výchozí snímek dat při osamostatnění projektu; živá data a novější archiv vznikají v publikačním repozitáři webu.

Upravený kód se na veřejném webu projeví při příštím úspěšném společném redakčním cyklu. Okamžité nasazení lze spustit ručně v Actions repozitáře webu. Není potřeba osobní přístupový token ani další kopie automatizace.

## Vyhledávání

Zadání dotazu prohledává aktuální data i všechna uložená vydání z `archive/index.json`, bez 24hodinového omezení. Archiv se načítá až při hledání, čtyřmi souběžnými požadavky, a během návštěvy zůstává v paměti. Výpadek je viditelný a lze jej opakovat. Hledá se v titulku, shrnutí, celém rozboru a názvu zdroje; nikoli v plném textu externího článku. Bez diakritiky a velikosti písmen, se základním porovnáním koncovek (nikoli úplnou českou lemmatizací); Letná/Letné/Letnou mají výslovnou shodu bez záměny s „letní“. Více slov musí být nalezeno v témže článku. Shodné URL napříč vydáními se slučují, přednost má nejlépe odpovídající verze, při shodě nejnovější. Lze řadit podle relevance nebo data vydání a filtrovat rubriku. Zrušení hledání vrací vybrané vydání. Tematické štítky ani externí plné texty se zatím neindexují.

Regresní kontrola vyhledávání: `node scripts/test_search.cjs` (bez dalších závislostí).


## Společný redakční cyklus (11. 11. 2026)

Pravidelný sběr i rozbory řídí jedna hodinová úloha ChatGPT „Sběr a rozbory Politického přehledu“. Samostatný cron v publikačním repozitáři je vypnutý; GitHub workflow zůstává pouze pro ruční obnovu (ta sama AI rozbory nespouští). Provoz nepoužívá placené AI API. Zpoždění či limit ChatGPT může opozdit celý cyklus, nejde o službu s garantovanou dobou.

Pracovní postup je v `scripts/EDITORIAL_CYCLE.md`. `collect_cycle.py` připraví novou edici v pracovní kopii, která se ihned publikuje ještě před rozbory. Články s nedostatečným podkladem zůstávají veřejné. Rozbory se doplňují postupně a ukládají do `impact_notes.json`; shodná URL a titulek umožní opětovné použití. Sběr přebírá rovněž hotové rozbory poslední živé edice. Poznámky se automaticky nemažou po 72 hodinách.

`analysis_progress.py` zaznamenává skutečný začátek a dokončení zpracování. Živý `analysis-progress.json` uchovává posledních 50 měření. Odhad používá medián alespoň pěti dokončených zpracování a pozici ve frontě; jde o orientační údaj, nikoli zaručený termín. Při stáří heartbeat nad 10 minut, uplynulém odhadu, nedostatku měření nebo v archivu se čas neslibuje. Záznamy s nedostatečnými zdroji uvádějí, že ověřování pokračuje. Ukončení úlohy ruší odhady. Čas sběru a archiv se při doplňování rozborů nemění.
