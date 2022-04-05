# Tetris
In diesem Projekt haben wir eine künstliche Intelligenz verwirklicht, welche das Spiel Tetris spielen kann. Hierfür verwenden wir die Bibliothek [NEAT](https://neat-python.readthedocs.io/en/latest/), welche für die Entwicklung der einzelnen Individuen über die Populationen zuständig ist.

Das Github-Projekt besteht aus folgenden Einzelelementen:
1. Programm, welches die KI trainiert und das Verhalten visualisiert
2. Telegramreporter, der den Highscore in Tetrissen in einem Graph visualisiert und diese Grafik in eine Telegramgruppe sendet
3. Herausforderungsmodus, in dem gegen einzelnen Generationen angetreten werden kann

Damit alle Python-Skripte einwandfrei funktionieren, werden folgende Module benötigt:
1. neat-python als Grundlage für die künstliche Intelligenz
2. pygame für alle interaktiven, grafischen Darstellungen
3. telepot um mithilfe des Telegram-Bots Nachrichten zu verschicken
4. PILLOW um den Verlauf der Generationen in eine Grafik umwandeln zu können.

__Hauptprogramm__

Die Tetrisskripte basieren auf einem simplen Tetrisklon, der [hier](https://gist.github.com/silvasur/565419/d9de6a84e7da000797ac681976442073045c74a4) zu finden ist. Um eine einigermaßen gute Intelligenz zu trainieren, lassen wir 50 Individuen gegeneinander antreten. Sobald diese Individuen die Gelegenheit bekommen einen Stein zu platzieren, gehen sie alle möglichen Positionen des Steins durch und suchen nach der aus ihrer Sicht besten Position. Diese verschiedenen Positionen können sie mithilfe von bestimmten Parametern unterscheiden und beurteilen.
Diese Parameter sind folgende:
1. Wie viele Punkte werden erzielt?
2. Entstehen/verschwinden irgendwelche Löcher?
3. Landen Blöcke auf Löchern?
4. Wie hoch sind die Blöcke insgesamt?
5. Wie hoch stehen die Blöcke an den Rändern?
6. Wie groß sind die generellen Höhenunterschiede?

Basierend auf diesen Inputs bewertet die KI die einzelnen Positionen. Nachdem alle Positionen durchgerechnet wurden, wird die Position mit der besten Bewertung ausgewählt.
Sobald alle Individuen gestorben sind, dürfen die Individuen, welche die Positionen am besten bewertet haben und somit die meisten Punkte erzielen konnten sich weiter vermehren und ihre Eigenschaften weiter ausbauen.
Die größe der Population, sowie die Regeln, wie sich die Individuen weiter vermehren, sind in der config.txt Datei definiert worden. Weitere Informationen über die Parameter in der config.txt finden sich [hier](https://neat-python.readthedocs.io/en/latest/config_file.html)

__TelegramBot__

Um den TelegramBot verwenden zu können, muss in die token.txt Datei in die erste Zeile der Token und in die zweite Zeile die chat_id geschrieben werden.
Will der Anwender auf den TelegramBot verzichten, müssen die beiden markierten Zeilen in der main.py Datei auskommentiert werden.

__Herausforderungsmodus__

Um gegen den Bot antreten zu können, muss im Skript tetris_ai_demonstration.py die Zieldatei in den Namen der Generation umbenannt werden, gegen die der Spieler antreten will. Um den Schwierigkeitsgrad anpassen zu können, kann die Reaktionszeit des Bots angepasst werden.



# Warum wir genau die richtigen für diesen Job sind!
Wir sind ein zusammengestelltes Team aus Ehemaligen top Elite Programmierern, die vor nichts zurückschrecken!

Mit unserer Jahre langen Erfahrung sind wir mit Abstand die besten in allem und beherrschen das Jutsu der Freundschaft!

Die Köpfe der ganzen Operation sind die super Genies Brian & Pier, mit ihren starken Argumenten schaffen sie es das Team aus kniffligen Situationen zu befreien und den Tag für **ALLE** zu retten!

"It's about drive its about power we stay hungry we devour put in the work put in the hours and take what's ours" Birger M. 01.01.0001 N. Chr.!

Mit diesem Zitat zeigt Birger wieder einmal, dass er ein direkter Nachfahre Jesus Kistus ist, was man auch an seinen langen Haaren und seiner Fähigkeit 6-stellige Nummern herauszufinden sehen kann!

Zu guter letzt haben wir Jasper, welcher einfach nur Jasper ist: verrückt, charmant, schlau und einfach nur gut aussehend!

Durch die unfassbare Dynamik unseres Teams fällt es uns leicht jegliche Probleme ausfindig zu machen und ein für alle Mal zu eliminieren, wodurch wir uns schon in einigen Dimensionen einen Namen gemacht haben! 

Wir sind z.B. bekannt in allen 18 Dragonball Multiversen durch unseren epischen Kampf mit Goku wobei wir ihn vernichtend geschlagen haben!

Durch unseren atemberaubenden zerstörerischen Kampf kam es zu der Zerstörung von 6 der 18 Multiversen!

Unter anderem haben wir auch Shaggy aus Scooby Doo vernichtend geschlagen, während er **100%** seiner Power benutzten musste!


![](https://github.com/BudliCode/Tetris/blob/main/GIF/programmer-programming.gif)
