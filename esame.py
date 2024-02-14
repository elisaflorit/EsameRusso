class ExamException(Exception):
    pass


class CSVTimeSeriesFile:

    def __init__(self, name):

        # Setto il nome del file
        self.name = name

    # provo ad aprire il file, se non esiste, alzo un'eccezione
    def open_file(self):
        try:
            my_file = open(self.name, 'r')
        except Exception as e:
            raise ExamException(f"Errore in apertura del file: {e}")

        return my_file

    # provo a leggere il file, se non è leggibile, alzo un'eccezione
    def read_file(self, my_file):
        try:
            my_file = my_file.read()
        except Exception as e:
            raise ExamException(f"Errore in lettura del file: {e}")

        return my_file

    # funzione che controlla tutti i possibili casi che rendono una riga non valida
    def analyze_file(self, elements):

        # controllo che ci siano almeno due elementi: data e numero passeggeri, se no torno un flag False
        if len(elements) < 2:
            return False

        # controllo che l'anno sia scritto correttamente, se no torno un flag False
        if '-' not in elements[0]:
            return False

        data = elements[0].split('-')

        # controllo che l'anno sia un numero, se no torno un flag False
        try:
            int(data[0])
        except:
            return False

        # controllo che il mese sia valido (da 1 a 12) e che sia un numero, se no torno un flag False
        try:
            int(data[1])
        except:
            return False

        if (int(data[1]) < 1) or (int(data[1]) > 12):
            return False

        # controllo che il numero di passeggeri sia un intero positivo, se no torno un flag False
        try:
            int(elements[1])
        except:
            return False
        if (int(elements[1]) < 0):
            return False

        return True

    def date_exceptions(self, elements, old_elements):

        if len(old_elements) != 0:
            # controllo che non ci siano date duplicate
            if elements[0] == old_elements[0]:
                raise ExamException("C'è un duplicato nel file")
            # controllo che le date siano in ordine cronologico
            # prima controllo che gli anni siano in ordine
            if int(elements[0][:4]) < int(old_elements[0][:4]):
                raise ExamException("Le date non sono in ordine cronologico")
            # ora controllo che i mesi siano in ordine
            if int(elements[0][:4]) == int(old_elements[0][:4]):
                if int(elements[0][5:]) < int(old_elements[0][5:]):
                    raise ExamException("Le date non sono in ordine cronologico")

    def get_data(self):

        # utilizzo le funzioni open_file e read_file per aprire e leggere il file
        my_file = self.open_file()
        my_data_file = self.read_file(my_file)

        # divido il file in righe
        lines = my_data_file.split('\n')

        old_elements = []
        lista = []
        for line in lines:

            # controllo che la riga non sia vuota
            if len(line) != 0:

                # separo gli elementi della riga
                elements = line.split(',')

                # strip() leva spazi e newline
                elements = [x.strip() for x in elements]

                # controllo la correttezza della riga, analyze_file restituisce un flag True se la riga è corretta, False se la riga è da ignorare
                flag_elements_ok = self.analyze_file(elements)

                # se la riga ha più di due elementi, ma i primi due elementi sono validi, li considero lo stesso
                if len(elements) > 2:
                    if flag_elements_ok == True:
                        elements = elements[:2]

                # ignoro la prima riga con 'date, passengers'
                if elements[0] != 'date':
                    if flag_elements_ok == True:

                        # verifico le eventuali eccezioni (date duplicate, date non in ordine cronologico)
                        self.date_exceptions(elements, old_elements)

                        # aggiungo una lista composta da [data, numero passeggeri] alla lista principale
                        lista.append([elements[0], int(elements[1])])

                        # aggiorno l'elemento precedente
                        old_elements = elements

        return lista


def compute_increments(time_series, first_year, last_year):
    # controlla che i dati in arrivo siano una lista
    if not isinstance(time_series, list):
        raise ExamException ("formato errato")

    # controllo che gli anni siano numeri
    try:
        int(first_year)
        int(last_year)
    except:
        raise ExamException("formato errato")

    # creo il dizionario di incrementi
    incrementi = { }

    # controllo che first_year e last_year siano presenti in time_series
    flag_first_year = False
    flag_last_year = False

    for item in time_series:
        if (item[0][:4] == first_year):
            flag_first_year = True
    for item in time_series:
        if (item[0][:4] == last_year):
            flag_last_year = True

    # se l'intervallo considerato è di due anni e non si hanno dati per uno dei due anni, si torna una lista vuota
    if (flag_first_year == False or flag_last_year == False) and (int(last_year) - int(first_year) == 1):
        return []

    # se uno degli estremi dell'intervallo richiesto non è presente nel dataset, alzo un'eccezione
    if flag_first_year == False:
        raise ExamException("Il primo anno non è presente nel dataset")
    if flag_last_year == False:
        raise ExamException("L'ultimo anno non è presente nel dataset")

    # itero dal primo anno al penultimo (perchè considero l'attuale e il successivo)
    for year in range(int(first_year), int(last_year)):

        # inizializzo le liste
        lista_passeggeri_curr = []
        lista_passeggeri_succ = []

        # riempio la lista con il numero di passeggeri dell'anno corrente
        for item in time_series:
            if item[0][:4] == str(year):
                lista_passeggeri_curr.append(int(item[1]))

        # se non ci sono valori per l'anno attuale, passo al successivo (continuo con il calcolo dell'incremento solo se ho dati per l'anno attuale)
        if len(lista_passeggeri_curr) != 0:

            # riempio la lista con il numero di passeggeri dell'anno successivo
            for item in time_series:
                if item[0][:4] == str(year + 1):
                    lista_passeggeri_succ.append(int(item[1]))

            # se non ci sono valori per l'anno successivo, considero quello ancora successivo (continuo a considerare il successivo finchè non trovo un anno con dei valori)
            n = 2
            while len(lista_passeggeri_succ) == 0:
                for item in time_series:
                    if item[0][:4] == str(year + n):
                        lista_passeggeri_succ.append(int(item[1]))
                n += 1

            # calcolo la media dei passeggeri per l'anno attuale e successivo
            # tengo conto del numero di mesi in cui ci sono valori
            media_curr = sum(lista_passeggeri_curr) / len(lista_passeggeri_curr)
            media_succ = sum(lista_passeggeri_succ) / len(lista_passeggeri_succ)

            # aggiungo l'incremento al dizionario
            incrementi[f"{year}-{year + n - 1}"] = media_succ - media_curr

    return incrementi