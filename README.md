# Translator
## Content
1. How it's works?
2. Installation
3. GUI
4. To Do ...

## How it's Works?
This python based program is designed to translate some foreign languages to Persian. Current version is translating English to Persian and using this 2 models :    
1. Google Translate
2. ChatGPT(with API Key)

Input and Output format is :
- Input  format : DocX 
- Output Format : DocX

**Note : If Input format is PDF , must be converted to DocX format (prefered app to convert : Foxit Phantom)**

To handle the docx file we used python-docx library, this library iterate on docx file and translte base on 2 iteration loop : 
1. Iterate on paragraphs    
Get each paragraph and send it to translator. Below is src code :
```py
translate_paragraphs():
    # Translate paragraphs
    para_count = len(doc.paragraphs)
    counter = 0
    for para in track(doc.paragraphs, description="[green]Translating paragraphs..."):  
        if para.text == "":
            continue
        if progress_callback:
            counter += 1
            progress_callback(counter / para_count * 50,"Translating paragraphs")      
        print(f"Paragraph: {para.text}")
        for i in range(1,3): # this loop is for translator model error, try 3 times if we face error
            try:
                translated = translator.translate(para.text)  
                print(Fore.WHITE)
                break
            except:
                print(Fore.RED + Style.BRIGHT + "Translation error, retrying...")
                time.sleep(1)
                continue
        
        if translated:
            para.text = translated
            set_paragraph_direction(para, direction="RTL")       
            set_runs_rtl_and_font(para)   
```
Iterate on tables is like paragraphs with some changes.

2. Configuration 

At the begining of code there are some options to set the program :
```py
font_name = 'B Nazanin' 
translator_name = "google"  # google, deepl, chatgpt
font_size = 11
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
translators = {
    "google": lambda src,tgt: GoogleTranslator(source=src,target=tgt),
    "deepl": lambda src,tgt: DeeplTranslator(api_key="YOUR_KEY", target=tgt, source=src),
    "chatgpt": lambda src,tgt: ChatGptTranslator(api_key=OPENAI_API_KEY , target=tgt,source=src,model="gpt-5.1"),
}
output_format = "docx"
```

3. There are some codes that are for Right to Left languages and to be sure ouput doc is be i right font and format.   
To find these methods i used some creative methods : 
    1. Extract xml structured of DocX file with convert the docx to zip and then extract it with WinRAR    
    ![image](./img/WordFile_Structure.PNG)
    2. Make some changes to to original doc and analyze changes in extracted files (i've used NotePad++ to track the changes and compare files). With this method i found how change the xml elements to set font, rtls for runs and so on.

    > ***Notes :***    
    ***Runs :*** Paragraphs contain text runs, which are continuous segments of text sharing the same formatting. 


```py
def set_run_rtl(run):
    r = run._r
    rPr = r.get_or_add_rPr()
    bidi = OxmlElement('w:rtl')  
    rPr.append(bidi)

def set_run_font(run,font_name,font_size):
    try:
        run.font.name = font_name
        run.font.size = Pt(font_size)
        rPr = run._element.get_or_add_rPr()
        rFonts = rPr.rFonts     
        rFonts.set(qn('w:cs'), font_name)
    except Exception as e:
        print(Fore.RED + Style.BRIGHT + "Error setting font for run")
        pass
    
# Set to correct english-persian paragraphs
def set_runs_rtl_and_font(paragraph):
    for run in paragraph.runs:
        set_run_rtl(run)
        set_run_font(run,font_name,font_size)



def set_paragraph_direction(paragraph, direction="LTR"):
    pPr = paragraph._p.get_or_add_pPr()

    # remove existing bidi element
    for el in pPr.xpath('./w:bidi'):
        pPr.remove(el)

    bidi = OxmlElement('w:bidi')
    bidi.set(qn('w:val'), "1" if direction.upper() == "RTL" else "0")
    pPr.append(bidi)   
```

## Installaion

At this level there is 2 option to use this program :
1. Using source code (both ChatGPT and Google Translate) 
2. Using executable file that is generatged with PyIstaller library (Curentlly this method can use just Google Translate)

```py
pip install pyinstaller

# locate the python scripts directory and run this command in cmd or powershell
python -O  -m pyinstaller --onefile --icon=icon.ico Translator.py 
# --onefile is important to create just one executable
# -O is for optimization
```

>***Note:*** Run this command in bin directory for cleanness!! :). Executable is in bin/dist directory

## GUI 
I designed a GUI for this app with `tkinter` that is simple but can set some features for translator.
![image](./img/GUI.png)


To run this GUI just run it in GUI.py file.

## TO DO

1. PDF to Docx and vice versa (PDF2Docx and DocX2PDF are some options)
2. Add more Options as Translator (Inter Models like NLLB (No Language Left Behind from face book) and Microsoft and so on)
3. Add a Webserver or Bale Bot for Users to work with it smoothly  (python + FastAPI)
4. Integrate Local model Translations with Onlines with Integrated Web Interface 
5. Auto Detect source laguage 
6. Add a Logger 
7. Download some Datasets for Translation Ranking (What model is best in persian Translation , do like this for Persian OCR). There are some links in Chrome bookmarsk for this purpuses. [link1](https://huggingface.co/datasets/shenasa/English-Persian-Parallel-Dataset/viewer/default/train?views%5B%5D=train) and [link2](https://huggingface.co/datasets/persiannlp/parsinlu_translation_en_fa)






