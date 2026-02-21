# Local Translator

## Contents
1. NLLB
2. To Do

## [NLLB : No Language Left Behind][1]

NLLB: No Language Left Behind is a multilingual translation model. It’s trained on data using data mining techniques tailored for low-resource languages and supports over 200 languages. NLLB features a conditional compute architecture using a Sparsely Gated Mixture of Experts.

### [Types][1]
1. NLLB-200-distiled-600M 
2. NLLB-200-distiled-1.3B
3. NLLB-200-3.3B

### How to use it?

The best referece for how to use is [origninal reference][3]

### My choosen method

```py
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("facebook/nllb-200-distilled-600M")
model = AutoModelForSeq2SeqLM.from_pretrained("facebook/nllb-200-distilled-600M", dtype="auto", attn_implementation="sdpa")

article = "UN Chief says there is no military solution in Syria"
inputs = tokenizer(article, return_tensors="pt")

translated_tokens = model.generate(
    **inputs, forced_bos_token_id=tokenizer.convert_tokens_to_ids("fra_Latn"), max_length=30
)
print(tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[0])
```

## To Do
1. Find a dataset to evaluate the model for transaltion
2. How Run this model in a way to work with OpenAI API
3. Integrate Online Translator code with Local Translator

## Reference
[1]: https://huggingface.co/facebook/models?search=nllb
[2]: https://huggingface.co/facebook/nllb-200-distilled-600M
[3]: https://huggingface.co/docs/transformers/en/model_doc/nllb

