#!/usr/bin/env python3
import sys
import os
import re
import shutil

def clean_file(file_path):
    if not os.path.exists(file_path):
        print(f"Fehler: Datei '{file_path}' nicht gefunden.")
        sys.exit(1)

    with open(file_path, "r", encoding="utf-8") as infile:
        zeilen = infile.readlines()

    bereinigte_zeilen = []
    aenderungen_vorgenommen = False

    # KORREKTUR: Dreifache Anführungszeichen verhindern den SyntaxError bei den einfachen Anführungszeichen
    kommentar_regex = re.compile(r"""("[^"]*"|'[^']*')|(#.*)""")

    for index, zeile in enumerate(zeilen, start=1):
        # Fall 1: Reine Kommentarzeilen (auch eingerückt) -> Automatisch löschen
        if zeile.lstrip().startswith("#"):
            aenderungen_vorgenommen = True
            continue

        # Fall 2: Kommentare am Ende von Codezeilen
        match = kommentar_regex.search(zeile)
        if match and match.group(2):
            kommentar_start = match.start(2)
            vorderer_teil = zeile[:kommentar_start].rstrip()
            neue_zeile = vorderer_teil + "\n" if vorderer_teil else "\n"

            print(f"\n[Zeile {index}] KOMMENTAR AM ENDE GEFUNDEN:")
            print(f"  Alt: {zeile.rstrip()}")
            print(f"  Neu: {neue_zeile.rstrip()}")

            entscheidung = input("  Kürzen? (j/n): ").strip().lower()
            if entscheidung == 'j':
                bereinigte_zeilen.append(neue_zeile)
                aenderungen_vorgenommen = True
            else:
                bereinigte_zeilen.append(zeile)
        else:
            bereinigte_zeilen.append(zeile)

    # Nur verarbeiten und speichern, wenn Änderungen vorliegen
    if aenderungen_vorgenommen:
        # Erstelle den Backup-Dateinamen (z.B. aaa.py -> aaa_orgi.py)
        basis_pfad, datei_endung = os.path.splitext(file_path)
        backup_pfad = f"{basis_pfad}_orgi{datei_endung}"

        try:
            # Kopiert die originale Datei als Backup
            shutil.copy2(file_path, backup_pfad)
            print(f"\nSicherheitskopie erstellt: {backup_pfad}")

            # Überschreibt das Original mit den bereinigten Zeilen
            with open(file_path, "w", encoding="utf-8") as outfile:
                outfile.writelines(bereinigte_zeilen)
            print("Originaldatei erfolgreich aktualisiert.")

        except Exception as e:
            print(f"Fehler beim Speichern oder Sichern: {e}")
    else:
        print("\nKeine Änderungen an der Datei vorgenommen. Es wurde kein Backup erstellt.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Nutzung: clean_comments.py <pfad_zur_datei.py>")
        sys.exit(1)

    # Übergibt das korrekte Argument (Index 1) als String
    clean_file(sys.argv[1])
