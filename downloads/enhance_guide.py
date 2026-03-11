# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, 'C:/Users/hkkchan/.claude/skills/docx')
from scripts.document import Document

doc = Document(
    'c:/Users/hkkchan/Downloads/KSFreePlayConference/downloads/activity_guide_unpacked',
    rsid="1027559C"
)

FONTS = '<w:rFonts w:ascii="Aptos" w:eastAsia="Microsoft JhengHei" w:hAnsi="Aptos"/>'

def sub_header(text):
    return f'''<w:p>
      <w:pPr><w:spacing w:line="240" w:lineRule="exact"/>
        <w:ind w:left="360"/>
        <w:rPr>{FONTS}</w:rPr>
      </w:pPr>
      <w:r><w:rPr>{FONTS}<w:b/><w:bCs/><w:color w:val="5A5A72"/>
        <w:sz w:val="20"/><w:szCs w:val="20"/>
      </w:rPr><w:t>{text}</w:t></w:r>
    </w:p>'''

def italic_prompt(text, numId=7, ilvl=1):
    return f'''<w:p>
      <w:pPr>
        <w:pStyle w:val="ListParagraph"/>
        <w:numPr><w:ilvl w:val="{ilvl}"/><w:numId w:val="{numId}"/></w:numPr>
        <w:spacing w:line="240" w:lineRule="exact"/>
        <w:rPr>{FONTS}</w:rPr>
      </w:pPr>
      <w:r><w:rPr>{FONTS}<w:i/><w:iCs/>
        <w:color w:val="555555"/>
        <w:sz w:val="20"/><w:szCs w:val="20"/>
      </w:rPr><w:t>{text}</w:t></w:r>
    </w:p>'''

def plain_item(text, numId=7, ilvl=1):
    return f'''<w:p>
      <w:pPr>
        <w:pStyle w:val="ListParagraph"/>
        <w:numPr><w:ilvl w:val="{ilvl}"/><w:numId w:val="{numId}"/></w:numPr>
        <w:spacing w:line="240" w:lineRule="exact"/>
        <w:rPr>{FONTS}</w:rPr>
      </w:pPr>
      <w:r><w:rPr>{FONTS}
        <w:sz w:val="20"/><w:szCs w:val="20"/>
      </w:rPr><w:t>{text}</w:t></w:r>
    </w:p>'''

def italic_para_a2(text):
    return f'''<w:p>
      <w:pPr><w:spacing w:line="240" w:lineRule="exact"/>
        <w:ind w:left="360"/>
        <w:rPr>{FONTS}</w:rPr>
      </w:pPr>
      <w:r><w:rPr>{FONTS}<w:i/><w:iCs/>
        <w:color w:val="555555"/>
        <w:sz w:val="20"/><w:szCs w:val="20"/>
      </w:rPr><w:t>{text}</w:t></w:r>
    </w:p>'''

# ─────────────────────────────────────────────────────────────────
# ACTIVITY 1 · Step 2: 提出挑戰
# Insert prompting direction after "巡迴各組，以提問引導挑戰生成"
# ─────────────────────────────────────────────────────────────────
node = doc["word/document.xml"].get_node(tag="w:r", contains="以提問引導挑戰生成")
doc["word/document.xml"].insert_after(node.parentNode,
    sub_header("【引導方向】") +
    italic_prompt("引導小組將挑戰具體化至某一真實場景（而非停留於籠統感受）") +
    italic_prompt("鼓勵小組橫跨多個CPS維度思考，避免挑戰全部集中同一範疇")
)

# ─────────────────────────────────────────────────────────────────
# ACTIVITY 1 · Step 4: 整合分析
# Insert direction after "提醒聚焦於可控範圍內的解決方案"
# ─────────────────────────────────────────────────────────────────
node = doc["word/document.xml"].get_node(tag="w:r", contains="提醒聚焦於可控範圍內的解決方案")
doc["word/document.xml"].insert_after(node.parentNode,
    sub_header("【引導方向】") +
    italic_prompt("協助小組區分「可以即時改變的」與「需要系統支持的」障礙，優先聚焦前者") +
    italic_prompt("鼓勵解決方案具體到「明天返校即可試行」的程度") +
    italic_prompt("連結CPS維度時，引導小組思考方案如何改善小朋友特定方面的遊戲體驗，而非只停留於執行層面")
)

# ─────────────────────────────────────────────────────────────────
# ACTIVITY 1 · Step 5: 全場分享
# Insert sharing direction after "邀請五個小組進行站立分享（每組1分鐘）"
# Find "邀請五個小組進行站立分享" - text is split, search around line 2100
# ─────────────────────────────────────────────────────────────────
node = doc["word/document.xml"].get_node(tag="w:r", contains="邀請五個小組進行站立分享")
doc["word/document.xml"].insert_after(node.parentNode,
    sub_header("【分享引導方向】") +
    plain_item("串連各組：帶領員的角色是「主持人兼串連者」——點出不同組之間的共同困難或相近方向") +
    plain_item("突出可控的改變：引導全場看到，教師每日的小決定（何時介入、何時退後）本身就是推動自由遊戲的核心行動") +
    plain_item("重新定位教師角色：協助討論「不介入」本身是一種專業判斷，非放任") +
    plain_item("鼓勵正向氛圍：避免討論停留於「系統問題無從改變」的無力感，引導至「我能做的第一步」")
)

# ─────────────────────────────────────────────────────────────────
# ACTIVITY 2 · Step 3: 分析注釋
# Insert direction after "「如何讓家長成為引導者？」" (line 4318)
# ─────────────────────────────────────────────────────────────────
node = doc["word/document.xml"].get_node(tag="w:r", contains="如何讓家長成為引導者")
doc["word/document.xml"].insert_after(node.parentNode,
    sub_header("【引導方向】") +
    italic_para_a2("引導小組以「遊戲性」眼光評估空間：重點在於空間是否讓小朋友主動探索、自由發揮，而非設施是否齊全") +
    italic_para_a2("引導小組思考家長的實際角色：怎樣由「監管者」轉化為「陪伴者」，在場但不主導") +
    italic_para_a2("提醒小組兼顧現實可行性：對普通家庭而言的交通、費用、時間等考量")
)

# ─────────────────────────────────────────────────────────────────
# ACTIVITY 2 · Step 5: 全場分享
# Insert direction after "引導簡短總結，突出各地區的共同主題或創新想法" (line 4631)
# ─────────────────────────────────────────────────────────────────
node = doc["word/document.xml"].get_node(tag="w:r", contains="引導簡短總結，突出各地區的共同主題")
doc["word/document.xml"].insert_after(node.parentNode,
    sub_header("【分享引導方向】") +
    italic_para_a2("串連各地區：點出不同地區的相似發現或對比，讓社區地圖成為集體知識，而非各組孤立的結論") +
    italic_para_a2("重塑城市遊戲的可能性：引導討論城市環境是有待發現的遊戲資源，而非自由遊戲的障礙") +
    italic_para_a2("強調教師作為橋樑：教師了解社區資源，可以如何幫助家長更有信心帶孩子出外探索") +
    italic_para_a2("地圖的延續價值：今日所建立的資源地圖，將成為教師與家長之間促進自由遊戲對話的工具")
)

doc.save()
print("Done!")
