#!/bin/bash
# Saved cards. Usage: presets.sh NAME [out.png]     (Python: $PY, default .venv/bin/python)
# Then preview with: $PY preview.py out.png
HERE="$(cd "$(dirname "$0")" && pwd)"
PY="${PY:-.venv/bin/python}"
OUT="${2:-$1.png}"
SF=/System/Library/Fonts/Supplemental
FU=$SF/Futura.ttc

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
  teide)
    # Ibarra Real Nova: revival of Joaquín Ibarra's 1780 Madrid types; Echeyde is the Guanche name
    $PY "$HERE/realtopo.py" "$OUT" \
      --source copernicus --lat 28.2257 --lon -16.625 --km 21 --interval 100 --major 500 --peak 0 \
      --local "El Teide" --local-font IbarraRealNova-Bold.ttf --local-index 0 --local-size 26 --local-tracking 1 \
      --local2 "Echeyde" --local2-font IbarraRealNova-Italic.ttf --local2-index 0 --local2-size 15 \
      --title "MOUNT TEIDE" --title-size 12 --sub "Tenerife · Canary Islands" --ornament pintadera --corner br \
      --label "peak|Pico Viejo|28.2640|-16.6643" --label "peak|Guajara|28.2165|-16.6118" \
      --label "italic|Las Cañadas|28.229|-16.625"
    ;;
  damavand)
    # Nastaliq is the Persian calligraphic hand; its tall line metrics need --local-dy
    $PY "$HERE/realtopo.py" "$OUT" \
      --source copernicus --lat 35.925 --lon 52.11 --km 18 --interval 200 --major 1000 --peak 0 \
      --minor-width 0.7 --major-width 1.6 \
      --local "دماوند" --local-font NotoNastaliqUrdu-Bold.ttf --local-index 0 --local-size 30 --local-tracking 0 --local-dy -27 \
      --title "MOUNT DAMAVAND" --title-size 12 --sub "Alborz · Iran" --ornament girih --corner bl
    ;;
  kotor)
    PT=/System/Library/Fonts/Supplemental/PTSans.ttc
    # Monomakh: early Cyrillic, after the Crnojević press at Cetinje (1494); hatched water reads apart from the
    # dense limestone contours better than water-lining in this narrow bay
    $PY "$HERE/realtopo.py" "$OUT" \
      --source copernicus --lat 42.465 --lon 18.745 --km 16 --interval 100 --major 500 --no-summit \
      --local "Бока которска" --local-font Monomakh-Regular.ttf --local-index 0 --local-size 22 --local-tracking 1 \
      --title "BAY OF KOTOR" --title-size 12 --sub "Adriatic · Montenegro" --ornament lion --corner tr \
      --water hatch --coast-width 1.2 \
      --label "place|Котор|42.4247|18.7712|font=$PT:7:10.5" --label "place|Пераст|42.4865|18.6987|font=$PT:7:10.5" \
      --label "place|Рисан|42.5153|18.6953|font=$PT:7:10.5" --label "italic|Которски залив|42.4718|18.7488|font=$PT:1:11" \
      --label "italic|Вериге|42.468|18.685|font=$PT:1:10.5" --label "summit|Ловћен 1,749|42.3990|18.8188|font=$PT:7:9.5"
    ;;
  moorea)
    FU=/System/Library/Fonts/Supplemental/Futura.ttc
    # coordinate pairs starting with a minus need "=", or argparse reads them as flags
    $PY "$HERE/realtopo.py" "$OUT" \
      --source copernicus --lat=-17.567 --lon=-149.835 --km 22 --interval 100 --major 500 \
      --summit=-17.5510,-149.8224 --peak 1207 \
      --local "Mo’orea" --local-font /System/Library/Fonts/Supplemental/Didot.ttc --local-index 2 --local-size 26 \
      --local-tracking 2 --local-bold 0.5 \
      --title "MOOREA" --title-size 12 --sub "1,207 m · French Polynesia" --ornament tatau \
      --water lines --north rose --north-corner br --cartouche-at=-17.66,-149.835 \
      --label "peak|Rotui|-17.5054|-149.8390" \
      --label "text|Opunohu|-17.466|-149.860|font=$FU:1:10.5" --label "text|Paopao|-17.479|-149.818|font=$FU:1:10.5"
    ;;
  cuillin)
    FU=/System/Library/Fonts/Supplemental/Futura.ttc
    # insular uncial for the Gaelic name; the DEM reads Sgùrr Dearg higher than Sgùrr Alasdair, so the summit
    # search is kept to 300 m; 50 m contours, dark on purpose: these are the Black Cuillin
    $PY "$HERE/realtopo.py" "$OUT" \
      --source copernicus --lat 57.205 --lon -6.165 --km 12 --interval 50 --major 250 \
      --summit "57.2071,-6.2231" --summit-radius 0.3 --peak 992 \
      --local "An Cuiltheann" --local-font UncialAntiqua-Regular.ttf --local-index 0 --local-size 18 --local-tracking 0 \
      --title "THE CUILLIN" --title-size 12 --sub "992 m · Isle of Skye, Scotland" --ornament knotwork --corner bl \
      --water lines --water-rings 3 \
      --label "peak|Sgùrr nan Gillean|57.2485|-6.1927|font=$FU:2:10.5" --label "peak|Blà Bheinn|57.2193|-6.0931|font=$FU:2:10.5" \
      --label "text|Loch Coruisk|57.2060|-6.1700|font=$FU:1:11" --label "text|Loch Scavaig|57.172|-6.137|font=$FU:1:10.5"
    ;;
  pingualuit)
    # Inuktitut syllabics; an impact crater lake in the tundra; 10 m contours for the 160 m rim
    $PY "$HERE/realtopo.py" "$OUT" --source copernicus --lat 61.2632 --lon -73.66 --km 8 --interval 10 --major 50 --no-summit \
      --local "ᐱᖑᐊᓗᐃᑦ" --local-font NotoSansCanadianAboriginal-Bold.ttf --local-index 0 --local-size 24 --local-tracking 1 \
      --title "PINGUALUIT CRATER" --title-size 12 --sub "Nunavik · Québec, Canada" --ornament inuksuk --water hatch \
      --cartouche-at "61.234,-73.66" --label "text|Pingualuk|61.2766|-73.66|font=$FU:1:11"
    ;;
  ramon)
    # Frank Ruhl (the classic Hebrew book face); the long crater fits only at 30 km; heavy lines for sparse desert
    $PY "$HERE/realtopo.py" "$OUT" --source copernicus --lat 30.60 --lon 34.86 --km 30 --interval 100 --major 500 --no-summit --minor-width 0.7 --major-width 1.6 --coast-width 1.5 \
      --local "מכתש רמון" --local-font FrankRuhlLibre-Bold.ttf --local-index 0 --local-size 26 --local-tracking 0 \
      --title "MAKHTESH RAMON" --title-size 12 --sub "Negev · Israel" --ornament ibex --cartouche-at "30.49,34.86" \
      --label "place|Mitzpe Ramon|30.6106|34.8016"
    ;;
  paektu)
    # Korean and Chinese names for the mountain on the border; Heaven Lake named in both
    $PY "$HERE/realtopo.py" "$OUT" --source copernicus --lat 41.99 --lon 128.06 --km 14 --interval 50 --major 250 --peak 0 \
      --local "백두산" --local-font NotoSerifKR-Bold.ttf --local-index 0 --local-size 26 --local-tracking 2 \
      --local2 "长白山" --local2-font NotoSerifSC-Bold.ttf --local2-index 0 --local2-size 15 \
      --title "PAEKTU · CHANGBAI" --title-size 12 --sub "China – North Korea border" --ornament lattice --water hatch \
      --corner bl --label "text|천지 天池|42.006|128.056|font=NotoSerifKR-Bold.ttf:0:13"
    ;;
  stromboli)
    # Bodoni (Parma) + the ancient Greek name Strongyle; trinacria for Sicily
    $PY "$HERE/realtopo.py" "$OUT" --source copernicus --lat 38.775 --lon 15.218 --km 8 --interval 50 --major 250 --peak 0 \
      --local "Stromboli" --local-font LibreBodoni-Bold.ttf --local-index 0 --local-size 26 --local-tracking 1 \
      --local2 "Στρογγύλη" --local2-font $SF/Didot.ttc --local2-index 2 --local2-size 15 \
      --title "AEOLIAN ISLANDS" --title-size 12 --sub "Tyrrhenian Sea · Sicily, Italy" --ornament trinacria \
      --water lines --north rose --north-corner br --cartouche-at "38.748,15.218" \
      --label "place|Stromboli|38.8040|15.2370" --label "place|Ginostra|38.7840|15.1930" \
      --label "italic|Sciara del Fuoco|38.7950|15.1990"
    ;;
  gavarnie)
    # Occitan name in Garamond; the DEM smooths the cirque walls, so the frame is tight on the bowl
    $PY "$HERE/realtopo.py" "$OUT" --source copernicus --lat 42.705 --lon -0.02 --km 7 --interval 100 --major 500 --no-summit \
      --local "Gavarnia" --local-font EBGaramond-Bold.ttf --local-index 0 --local-size 26 --local-tracking 1 \
      --title "CIRQUE DE GAVARNIE" --title-size 11 --sub "Hautes-Pyrénées · France" --ornament occitan --corner tr \
      --label "peak|Le Taillon 3,144|42.6935|-0.0513" --label "place|Brèche de Roland|42.6907|-0.0332" \
      --label "peak|Marboré 3,248|42.6926|0.0126"
    ;;
  drakensberg)
    # Zulu name; no feature labels: the DEM maxima don't match named summits with confidence
    $PY "$HERE/realtopo.py" "$OUT" --source copernicus --lat -28.745 --lon 28.89 --km 11 --interval 100 --major 500 --no-summit \
      --local "uKhahlamba" --local-font $SF/Baskerville.ttc --local-index 4 --local-size 21 --local-tracking 1 \
      --title "THE AMPHITHEATRE" --title-size 12 --sub "Drakensberg · South Africa" --ornament beadwork --corner bl
    ;;
  wadirum)
    # Amiri named directly so its tall line metrics (and --local-dy) are the same on every system
    $PY "$HERE/realtopo.py" "$OUT" --source copernicus --lat 29.55 --lon 35.43 --km 20 --interval 100 --major 500 --no-summit \
      --local "وادي رم" --local-font Amiri-Bold.ttf --local-index 0 --local-size 24 --local-tracking 0 --local-dy -8 \
      --title "WADI RUM" --title-size 12 --sub "Valley of the Moon · Jordan" --ornament sadu --corner bl \
      --label "summit|Jebel Rum 1,734|29.5749|35.3954" --label "peak|Umm Ishrin|29.5876|35.4426" \
      --label "place|Rum|29.5770|35.4210"
    ;;
  machupicchu)
    # Quechua spelling in Cinzel; Wayna Pikchu reads low in the DEM (sheer pinnacle), so no height
    $PY "$HERE/realtopo.py" "$OUT" --source copernicus --lat -13.158 --lon -72.543 --km 7 --interval 100 --major 500 --no-summit \
      --local "Machu Pikchu" --local-font Cinzel-Bold.ttf --local-index 0 --local-size 20 --local-tracking 1 \
      --title "MACHU PICCHU" --title-size 12 --sub "Urubamba · Cusco, Peru" --ornament tocapu --corner br \
      --label "place|citadel|-13.1631|-72.5450" --label "peak|Wayna Pikchu|-13.1554|-72.5454" \
      --label "italic|Urubamba|-13.1493|-72.5529"
    ;;
  popoizta)
    # the Smoking Mountain and the White Woman; xicalcoliuhqui stepped fret
    $PY "$HERE/realtopo.py" "$OUT" --source copernicus --lat 19.10 --lon -98.70 --km 28 --interval 100 --major 500 --no-summit \
      --local "Popocatépetl" --local-font IbarraRealNova-Bold.ttf --local-index 0 --local-size 22 --local-tracking 0.5 \
      --local2 "Iztaccíhuatl" --local2-font IbarraRealNova-Italic.ttf --local2-index 0 --local2-size 16 \
      --title "THE TWO VOLCANOES" --title-size 11 --sub "Puebla · México" --ornament stepfret --corner bl \
      --label "summit|Popocatépetl|19.022|-98.628" --label "summit|Iztaccíhuatl|19.179|-98.642" \
      --label "place|Paso de Cortés|19.087|-98.648"
    ;;
  reunion)
    # the three cirques around Piton des Neiges; Creole lambrequins
    $PY "$HERE/realtopo.py" "$OUT" --source copernicus --lat -21.10 --lon 55.48 --km 26 --interval 200 --major 1000 --peak 0 \
      --local "Piton des Neiges" --local-font $SF/Didot.ttc --local-index 2 --local-size 19 --local-tracking 0.5 --local-bold 0.5 \
      --title "LA RÉUNION" --title-size 12 --sub "Indian Ocean · France" --ornament lambrequin --corner br \
      --label "italic|Cilaos|-21.135|55.470" --label "italic|Mafate|-21.060|55.425" --label "italic|Salazie|-21.045|55.525"
    ;;
  taranaki)
    # the cone and its ring plain; kowhaiwhai koru scrolls
    $PY "$HERE/realtopo.py" "$OUT" --source copernicus --lat -39.30 --lon 174.06 --km 28 --interval 100 --major 500 --peak 0 \
      --local "Taranaki Maunga" --local-font $SF/Palatino.ttc --local-index 2 --local-size 19 --local-tracking 0.5 \
      --title "MOUNT TARANAKI" --title-size 12 --sub "Taranaki · Aotearoa New Zealand" --ornament kowhaiwhai --corner bl \
      --label "peak|Pouakai|-39.2382|174.0146" --label "peak|Kaitake|-39.1615|173.9660"
    ;;
  adamspeak)
    # Sinhala Sri Pada + Tamil Sivanolipatha Malai; lotus petal (pala pethi) bands
    $PY "$HERE/realtopo.py" "$OUT" --source copernicus --lat 6.825 --lon 80.535 --km 15 --interval 100 --major 500 --peak 0 \
      --local "ශ්‍රී පාද" --local-font NotoSerifSinhala-Bold.ttf --local-index 0 --local-size 24 --local-tracking 0 \
      --local2 "சிவனொளிபாதமலை" --local2-font NotoSerifTamil-SemiBold.ttf --local2-index 0 --local2-size 13 \
      --title "ADAM'S PEAK" --title-size 12 --sub "Central Highlands · Sri Lanka" --ornament lotus --water hatch --corner br \
      --label "text|Maussakele|6.8236|80.5536|font=$FU:1:10.5" --label "text|Castlereagh|6.8575|80.5867|font=$FU:1:10.5"
    ;;
  *)
    echo "usage: $0 NAME [out.png], NAME one of:"
    echo "  fuji matterhorn santorini kailash pyramiden ararat halong ilulissat teide damavand kotor moorea cuillin"
    echo "  pingualuit ramon paektu stromboli gavarnie drakensberg wadirum machupicchu popoizta reunion taranaki adamspeak"
    exit 1 ;;
esac
