# Bảng phân công đóng góp cá nhân — Đồ án KHDL chuyên đề 3

> Theo quy định đồ án: đóng gói 1 thành viên. Phân công theo trục (Data vs Model) để rõ ràng phạm vi trách nhiệm.

## Thành viên: [Điền tên] — MSSV: [Điền]

| Trục | Nhiệm vụ chính | File/Task | Hoàn thành |
|---|---|---|---|
| **Data** | Khởi tạo dự án + requirements.txt + README | Task 1 | ✅ |
| **Data** | Tạo nguồn dữ liệu thứ hai `neighborhood_amenities.csv` | Task 2 | ✅ |
| **Data** | Domain classes `PropertyListing`, `Location` | Task 3 | ✅ |
| **Data** | Cleaner: chuẩn hóa district, direction, lọc outlier | Task 4 | ✅ |
| **Data** | `PropertyDataManager`: load + clean + merge + save | Task 5 | ✅ |
| **Data** | Feature pipeline `ColumnTransformer` (impute + scale + OHE) | Task 6 | ✅ |
| **Model** | `PricePredictor`: Dummy + Linear + RF + GBR + CV | Task 7 | ✅ |
| **Model** | `KMeansSegmenter` + silhouette auto-pick K | Task 8 | ✅ |
| **Model** | `RecommendationEngine`: hybrid filter + score | Task 9 | ✅ |
| **Model** | Pipeline CLI end-to-end | Task 10 | ✅ |
| **Model** | Notebook 01 (problem + data) | Task 11.1 | ✅ |
| **Data** | Notebook 02 (collection + cleaning) | Task 11.2 | ✅ |
| **Data** | Notebook 03 (EDA + 10 biểu đồ) | Task 11.3 | ✅ |
| **Model** | Notebook 04 (ML + recommend demo) | Task 11.4 | ✅ |
| **Cả hai** | `data_dictionary.md` + `ai_usage_log.md` + báo cáo Markdown | Task 12 | ✅ |

## Lớp Python do thành viên phụ trách

Theo yêu cầu đồ án: "Mỗi thành viên phải có ít nhất một lớp Python do mình phụ trách".
Vì chỉ có 1 thành viên, tôi phụ trách toàn bộ 6 lớp:

| Lớp | File | Mô tả |
|---|---|---|
| `PropertyListing` | `src/domain.py` | Value object đại diện 1 tin đăng |
| `Location` | `src/domain.py` | Value object đại diện 1 vị trí |
| `PropertyDataManager` | `src/data_manager.py` | Quản lý load/clean/merge/save |
| `PricePredictor` | `src/predictor.py` | Mô hình dự đoán giá/m² |
| `KMeansSegmenter` | `src/segmenter.py` | Phân cụm K-Means + auto-pick K |
| `RecommendationEngine` | `src/recommender.py` | Hệ gợi ý top 5 |

## Công việc kiểm tra chéo

Vì chỉ có 1 thành viên, tôi dùng **TDD (Test-Driven Development)** để tự kiểm tra chéo:
- 35 test tự động (`pytest tests/ -v` → 35/35 PASS).
- Mỗi test kiểm tra hành vi cụ thể, đảm bảo code đúng chức năng.
- Pipeline chạy end-to-end kiểm tra tích hợp giữa các module.

## Phần trình bày

Theo yêu cầu "Mỗi thành viên trình bày tối thiểu 7 phút và trả lời câu hỏi về phần mình phụ trách": toàn bộ 7 phút × 1 người = 7 phút trình bày + Q&A.