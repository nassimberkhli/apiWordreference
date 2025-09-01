def print_translations(translations, colors=""):
    for value in translations.values():
        print ("\033[92m" + value['word'] + "\033[00m", '\t' , value['definition'])
        for meaning in value["meanings"]:
            print("\033[96m" + meaning + "\033[00m")
        for examples_list in value["examples"]:
            for example in range(len(examples_list)):
                if not example:
                    print("\033[91m" + " \u2022 " + "\033[00m" + examples_list[example])
                else:
                    print("\033[93m   " + examples_list[example] + "\033[00m")
        print('_' * 80)

def print_examples(translations):
    for value in translations.values():
        for examples_list in value["examples"]:
            for example in range(len(examples_list)):
                if not example:
                    print("\033[91m" + " \u2022 " + "\033[00m" + examples_list[example])
                else:
                    print("\033[93m   " + examples_list[example] + "\033[00m")

def download_audio(word, links):
    for audio_link in links:
        file = requests.get(audio_link)
        if file.status_code == 200:
            open(word + '-' + audio_link.rsplit('/', 2)[1] + '.mp3', 'wb').write(file.content)
