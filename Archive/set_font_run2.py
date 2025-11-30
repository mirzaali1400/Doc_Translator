import win32com.client as win32

# Open Word
word = win32.Dispatch("Word.Application")
word.Visible = True     # Optional

# Open your document
doc = word.Documents.Open(r"C:\Users\A2M\Desktop\Translator\output\IEC 62443-3-3 2013-13-15_translated_copilot.docx")

# Select all content
word.Selection.WholeStory()

# Apply Right-to-Left paragraph direction
# (equivalent to pressing the RTL Run button)
wdTextDirectionRTL = 2
word.Selection.ParagraphFormat.ReadingOrder = wdTextDirectionRTL
word.Selection.ParagraphFormat.BaseLineAlignment = 0  # optional cleanup

# Save
doc.SaveAs("output/test.docx")

# word.Quit()   # close when done
