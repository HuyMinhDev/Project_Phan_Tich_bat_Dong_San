# Bảng phân công đóng góp cá nhân — Đồ án KHDL chuyên đề 3

## Thành viên: [Nguyễn Minh Huy] — MSSV: [**2582003023**]

| Trục       | Nhiệm vụ chính                                                              | File/Task | Hoàn thành |
| ---------- | --------------------------------------------------------------------------- | --------- | ---------- |
| **Data**   | Khởi tạo dự án + requirements.txt + README                                  | Task 1    | ✅         |
| **Data**   | Tạo nguồn dữ liệu thứ hai`neighborhood_amenities.csv` (từ xlsx)             | Task 2    | ✅         |
| **Data**   | Domain classes`PropertyListing` (19 fields), `Location`                     | Task 3    | ✅         |
| **Data**   | Cleaner: chuẩn hóa district, decode direction/furnishing/legal, lọc outlier | Task 4    | ✅         |
| **Data**   | `PropertyDataManager`: load (CSV + XLSX) + clean + merge + save             | Task 5    | ✅         |
| **Data**   | Feature pipeline`ColumnTransformer` (impute + scale + OHE)                  | Task 6    | ✅         |
| **Model**  | `PricePredictor`: Dummy + Linear + RF + GBR + CV                            | Task 7    | ✅         |
| **Model**  | `KMeansSegmenter` + silhouette auto-pick K                                  | Task 8    | ✅         |
| **Model**  | `RecommendationEngine`: hybrid filter + score                               | Task 9    | ✅         |
| **Model**  | Pipeline CLI end-to-end                                                     | Task 10   | ✅         |
| **Model**  | Notebook 01 (problem + data căn hộ)                                         | Task 11.1 | ✅         |
| **Data**   | Notebook 02 (collection + cleaning)                                         | Task 11.2 | ✅         |
| **Data**   | Notebook 03 (EDA + 12 biểu đồ)                                              | Task 11.3 | ✅         |
| **Model**  | Notebook 04 (ML + 3 hồ sơ recommend demo)                                   | Task 11.4 | ✅         |
| **Cả hai** | `data_dictionary.md` + `ai_usage_log.md` + báo cáo Markdown                 | Task 12   | ✅         |

### 6 Lớp Python phụ trách

| Lớp                    | File                  | Mô tả                                          |
| ---------------------- | --------------------- | ---------------------------------------------- |
| `PropertyListing`      | `src/domain.py`       | Value object đại diện 1 tin đăng (19 fields)   |
| `Location`             | `src/domain.py`       | Value object đại diện 1 vị trí                 |
| `PropertyDataManager`  | `src/data_manager.py` | Quản lý load (CSV/XLSX) + clean + merge + save |
| `PricePredictor`       | `src/predictor.py`    | Mô hình dự đoán giá/m² (4 mô hình + CV)        |
| `KMeansSegmenter`      | `src/segmenter.py`    | Phân cụm K-Means + auto-pick K                 |
| `RecommendationEngine` | `src/recommender.py`  | Hệ gợi ý top 5 (hybrid filter)                 |

### Công việc kiểm tra chéo

Vì chỉ có 1 thành viên, em dùng **TDD (Test-Driven Development)** để tự kiểm tra chéo:

- **45 test tự động** (`pytest tests/ -v` → 45/45 PASS).
- Mỗi test kiểm tra hành vi cụ thể, đảm bảo code đúng chức năng.
- Pipeline chạy end-to-end kiểm tra tích hợp giữa các module.
