#!/bin/bash
# Saved cards. Usage: presets.sh NAME [out.png]     (Python: $PY, default .venv/bin/python)
# Then preview with: $PY preview.py out.png
HERE="$(cd "$(dirname "$0")" && pwd)"
PY="${PY:-.venv/bin/python}"
OUT="${2:-$1.png}"

case "$1" in
  fuji)
    $PY "$HERE/realtopo.py" "$OUT" \
      --lat 35.40 --lon 138.73 --km 28 \
      --local "富士山" --title "MOUNT FUJI" --sub "3,776 m · Honshu, Japan" --peak 3776
    ;;
  matterhorn)
    $PY "$HERE/realtopo.py" "$OUT" \
      --lat 45.9790 --lon 7.6586 --km 7 --source copernicus --swiss-patch 11 --interval 50 --major 500 \
      --local "Matterhorn" --local-font /System/Library/Fonts/Helvetica.ttc --local-index 1 --local-size 26 --local-tracking 0 \
      --title "CERVINO · CERVIN" --title-size 11 --sub "4,478 m · Valais / Valle d'Aosta" --peak 4478 \
      --emblem swiss --grid 1 --corner br --shade \
      --label "glacier|Matterhorngletscher|45.9905|7.6640" --label "glacier|Zmuttgletscher|45.9975|7.6420" \
      --label "glacier|Furgggletscher|45.9700|7.6800" --label "glacier|Tiefmattengletscher|45.9822|7.6395" \
      --label "hut|Hörnlihütte 3260|45.98236|7.67736" \
      --route "45.98236,7.67736;45.97636,7.65861"
    ;;
  santorini)
    AV="/System/Library/Fonts/Avenir Next.ttc"
    $PY "$HERE/realtopo.py" "$OUT" \
      --lat 36.413 --lon 25.405 --km 16.5 --source copernicus --interval 25 --major 100 \
      --local "ΣΑΝΤΟΡΙΝΗ" --local-font /System/Library/Fonts/Supplemental/Didot.ttc --local-index 2 --local-size 24 --local-tracking 2.5 --local-bold 0.5 \
      --title "SANTORINI · THERA" --title-size 11 --sub "Caldera of Thera · Cyclades, Greece" --peak 567 \
      --corner tr --ornament meander --water lines --north rose --north-corner bl \
      --label "place|Θήρα|36.4167|25.4317|font=$AV:2:11" \
      --label "place||36.4614|25.3756" --label "text|Οία|36.4745|25.3790|font=$AV:2:11" \
      --label "place|Ακρωτήρι|36.3567|25.4036|font=$AV:2:11" \
      --label "text|Θηρασιά|36.4630|25.3380|font=$AV:3:11" \
      --label "text|Νέα Καμένη|36.3915|25.3990|font=$AV:3:10.5" \
      --label "italic|Καλντέρα|36.423|25.405|font=$AV:6:11" \
      --label "italic|Αιγαίο Πέλαγος|36.333|25.44|font=$AV:6:11"
    ;;
  kailash)
    SF=/System/Library/Fonts/Supplemental
    $PY "$HERE/realtopo.py" "$OUT" \
      --lat 30.915 --lon 81.33 --km 38 --source copernicus --interval 100 --major 500 \
      --summit "31.0675,81.3119" --peak 6638 \
      --local "གངས་རིན་པོ་ཆེ" --local-font $SF/Kokonor.ttf --local-index 0 --local-size 26 --local-tracking 0 \
      --local2 "कैलाश पर्वत" --local2-font $SF/DevanagariMT.ttc --local2-index 1 --local2-size 15 \
      --title "MOUNT KAILASH" --title-size 12 --sub "6,638 m · Ngari, Tibet" \
      --ornament prayerflags --cartouche-at "30.899,81.24" --north-corner tr \
      --label "italic|Barkha Plain|30.885|81.425" \
      --label "text|མ་ཕམ་གཡུ་མཚོ|30.752|81.453|font=$SF/Kailasa.ttc:1:15" \
      --label "italic|Manasarovar|30.731|81.453" \
      --label "italic|Rakshastal|30.781|81.221"
    ;;
  pyramiden)
    PT=/System/Library/Fonts/Supplemental/PTSans.ttc
    $PY "$HERE/realtopo.py" "$OUT" \
      --lat 78.665 --lon 16.66 --km 24 --source copernicus --interval 100 --major 500 \
      --minor-width 0.75 --major-width 1.6 --coast-width 1.5 \
      --summit "78.6747,16.3517" --peak 0 \
      --local "ПИРАМИДА" --local-font $PT --local-index 2 --local-size 23 --local-tracking 1.2 \
      --title "PYRAMIDEN" --title-size 12 --sub "Billefjorden · Svalbard" \
      --emblem mining --water lines --water-rings 3 --cartouche-at "78.585,16.62" --north-corner tl \
      --label "place|Pyramiden|78.6556|16.3253|font=$PT:7:10.5" \
      --label "italic|Billefjorden|78.640|16.60|font=$PT:1:11" \
      --label "italic|Nordenskiöldbreen|78.667|16.96|font=$PT:6:10"
    ;;
  ararat)
    MS=/System/Library/Fonts/Supplemental/Mshtakan.ttc
    FU=/System/Library/Fonts/Supplemental/Futura.ttc
    # GLO-30 withholds the N39E044 tile (Armenia); GLO-90 is clean, terrarium has summit voids
    $PY "$HERE/realtopo.py" "$OUT" \
      --source copernicus90 --lat 39.684 --lon 44.348 --km 20 --interval 100 --major 500 \
      --summit "39.7017,44.2983" --peak 5137 \
      --local "Մասիս" --local-font $MS --local-index 2 --local-size 28 --local-tracking 2 --emblem eternity \
      --title "MOUNT ARARAT" --title-size 12 --sub "5,137 m · Ağrı Dağı, Türkiye" --corner bl --north-corner tr \
      --label "summit||39.6483|44.4142" \
      --label "text|Սիս|39.6275|44.432|font=$MS:2:14" --label "text|3,896|39.6205|44.432|font=$FU:2:9.5" \
      --label "italic|Ahora Gorge|39.752|44.352|font=$FU:1:11" \
      --label "italic|Serdarbulak|39.6644|44.3793|font=$FU:1:11"
    ;;
  halong)
    PA=/System/Library/Fonts/Supplemental/Palatino.ttc
    SO=/System/Library/Fonts/Supplemental/Songti.ttc
    AV="/System/Library/Fonts/Avenir Next.ttc"
    # hatched sea, white karst islands; water-lining around ~hundreds of islets turned into bubbles
    $PY "$HERE/realtopo.py" "$OUT" \
      --source copernicus --lat 20.865 --lon 107.135 --km 26 --interval 100 --major 200 \
      --water hatch --coast-width 1.2 --no-summit \
      --local "Vịnh Hạ Long" --local-font $PA --local-index 2 --local-size 22 --local-tracking 0.5 \
      --local2 "下龍灣" --local2-font $SO --local2-index 2 --local2-size 15 \
      --title "HA LONG BAY" --title-size 12 --sub "Gulf of Tonkin · Vietnam" --corner br --ornament dongson \
      --label "place|Hạ Long|20.951|107.080|font=$AV:2:11" \
      --label "text|Cát Bà|20.80|107.045|font=$AV:2:11.5"
    ;;
  ilulissat)
    BA=/System/Library/Fonts/Supplemental/Baskerville.ttc
    AV="/System/Library/Fonts/Avenir Next.ttc"
    # Copernicus flattens the fjord's ice melange to sea level: iceberg symbols (--ice) restore it
    $PY "$HERE/realtopo.py" "$OUT" \
      --source copernicus --lat 69.175 --lon -51.09 --km 22 --interval 50 --major 200 \
      --water lines --water-rings 2 --no-summit \
      --local "Ilulissat" --local-font $BA --local-index 4 --local-size 24 --local-tracking 1 --emblem greenland \
      --local2 "Kangerlua" --local2-font $BA --local2-index 5 --local2-size 15 \
      --title "ILULISSAT ICEFJORD" --title-size 11 --sub "Disko Bay · Greenland" --corner tl --north-corner tr \
      --ice "69.18,-51.06,69.12,-50.75,6.5" --ice "69.19,-51.27,69.11,-50.85,11,1" \
      --label "place|Ilulissat|69.2198|-51.0986|font=$AV:2:10.5" \
      --label "italic|Kangia|69.155|-50.90|font=$AV:3:12"
    ;;
  *)
    echo "usage: $0 fuji|matterhorn|santorini|kailash|pyramiden|ararat|halong|ilulissat [out.png]"; exit 1 ;;
esac
