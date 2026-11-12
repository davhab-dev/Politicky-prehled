# Úsporný analytický cyklus (vyvážený provoz)

Sběr, filtrování, archivaci a vydání článků provádí GitHub Actions každou hodinu přes
`davhab-dev/davhab-dev.github.io/.github/workflows/politicky-prehled.yml`.
AI nesmí tento sběr provádět ani přepisovat publikační repozitář.
Platí zákaz placeného AI API a zachování schválených českých zdrojů.

## Postup pro plánovanou automatizaci ChatGPT

1. Načti aktuální source main a živý `politicky-prehled/data.json` z publikačního main.
2. Proveď `python SOURCE/scripts/prepare_analysis_queue.py PUBLIC/politicky-prehled --limit 8`.
   Výstup obsahuje jen krátkou frontu, nikoliv celý archiv. Pokud nemáš lokální soubory,
   získej jen aktuální data a relevantní seznam uložených rozborů.
3. Přezkoumej maximálně osm unikátních událostí. Nezpracovávej již hotové a aktuální
   rozbory znovu; pokud je titulek nebo významně obsah změněn, ověř rozdíl. Dvě zprávy
   s podobnými slovy nemusí být stejnou událostí.
4. Čti dostupné věrohodné české podklady a podle potřeby primární dokumenty.
   Napiš konkrétní vlastní analýzu dopadů, podmínek a nejistot. Odděl doložená fakta,
   výroky a hypotézy. Zdroje dolož názvem a platným HTTPS odkazem.
5. Nové položky připoj do `scripts/impact_notes.json` ve zdrojovém main se
   zabezpečením proti souběžnému přepsání (SHA kontrola, při konfliktu znovu načíst).
   Zachovej existující rozbory; klíče jsou URL a kontroluje se přesný titulek.
6. **Nezapisuj do publikovaného HTML, data.json ani archivu.** Nezahajuj `collect_cycle.py`
   ani `analysis_progress.py`; další úspěšný hodinový sběr poznámky promítne.
7. Ohlásit pouze čísla: nově vytvořené, opětovně použité, odložené a trvalé chyby.
   Nikdy nepředstírat dokončený rozbor ani neslibovat dobu jeho publikace.

## Principy hodinového sběru

`collect_cycle.py` sestavuje edici, neaktivuje AI frontu a uchovává měření.
Každý úspěšný sběr publikuje bez čekání na komentáře. Sběr ani nasazení nesmí
odstranit dřívější archiv. Při selhání zůstane poslední funkční vydání.
Automatické publikování probíhá přes GitHub Actions a explicitní build GitHub Pages.

## Obnova a testy

Ověřit shodu vloženého JSON s data.json, archivní index, čas vydání a dostupnost
veřejné stránky. Před úpravami sběrače spustit Python unit testy a `node scripts/test_search.cjs`.
Ruční obnova je přes `workflow_dispatch` publikačního workflow.
