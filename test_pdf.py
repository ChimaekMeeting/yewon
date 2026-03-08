import pdfplumber
import os

pdf_path = "data/seoul_trail.pdf"
output_path = "extracted_text.txt"

if not os.path.exists(pdf_path):
    print(f"오류: {pdf_path} 파일을 찾을 수 없습니다.")
else:
    print(f"'{pdf_path}' 파일에서 전체 텍스트 추출을 시작합니다.")
    print("문서가 커서 시간이 다소 걸릴 수 있습니다. 잠시만 기다려주세요...")

    with pdfplumber.open(pdf_path) as pdf:
        with open(output_path, "w", encoding="utf-8") as f:

            total_pages = len(pdf.pages)

            # 작성해주신 전체 페이지 반복문 적용!
            for i in range(total_pages):
                page = pdf.pages[i]
                text = page.extract_text()

                f.write(f"========== [ {i+1} / {total_pages} 페이지 ] ==========\n")
                if text:
                    f.write(text + "\n\n")
                else:
                    f.write("(텍스트를 찾을 수 없습니다.)\n\n")

                # 10페이지를 처리할 때마다 터미널에 진행 상황을 알려줍니다.
                if (i + 1) % 10 == 0 or (i + 1) == total_pages:
                    print(f"... {i + 1} / {total_pages} 페이지 처리 완료 ...")

    print(
        f"✅ 전체 페이지 추출 완료! '{output_path}' 파일을 열어서 결과를 확인해보세요."
    )
