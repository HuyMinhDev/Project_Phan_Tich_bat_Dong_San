# Nhật ký sử dụng AI — Đồ án KHDL chuyên đề 3

> Nhật ký này được lập theo quy định đồ án (trang 23 của đề tài), ghi lại prompt, kết quả sử dụng và cách kiểm chứng/phản biện trong suốt quá trình thực hiện.

## 1. Môi trường sử dụng

- **Mô hình**: Cursor Agent (claude-fable-5)
- **Công cụ**: Cursor IDE + Claude
- **Phiên tổng**: 23/07/2026 → 08/08/2026 (17 ngày làm việc)

## 2. Phân loại mức sử dụng

Các lượt sử dụng AI được phân thành ba mức, dựa trên mức độ can thiệp vào sản phẩm cuối:

- **[HOC]** Tự học / nghiên cứu — học viên tự đọc tài liệu, tự đặt câu hỏi phân tích và tự đi đến kết luận. AI đóng vai trò trao đổi một chiều (hỏi–đáp khái niệm); không sinh mã nguồn.
- **[CODE]** AI hỗ trợ lập trình — học viên chốt phương án (thiết kế lớp, mapping, cấu trúc dữ liệu, outline). AI dựng mã theo đặc tả đã chốt. học viên chịu trách nhiệm rà soát, sửa lỗi và chạy kiểm thử.
- **[VIET]** AI hỗ trợ viết — học viên tự chuẩn bị nội dung chính. AI gợi ý cấu trúc đoạn văn, gợi ý cách diễn đạt, sửa lỗi chính tả; không thay đổi luận điểm.

Phân bổ ước lượng theo thời gian: [HOC] khoảng 45%, [CODE] khoảng 40%, [VIET] khoảng 15%. Con số này là ước lượnh chủ quan, dựa trên việc đối chiếu lại nhật ký prompt hằng ngày.

## 3. Bảng nhật ký theo ngày

| #   | Ngày       | Mức    | Công cụ      | Prompt (tóm tắt)                                                                                                                                                                                 | Kết quả AI trả về                                                                                                                             | Cách kiểm tra / quyết định của học viên                                                               |
| --- | ---------- | ------ | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| 1   | 2026-07-23 | [CODE] | Cursor Agent | "Update project theo data mới`real_estate_with_price_per.xlsx` (căn hộ 6 quận, không phải nhà phố 24 quận cũ)"                                                                                   | Đề xuất 3 hướng: rewrite theo Chuyên đề 3 (căn hộ); adapt lại code cũ; bỏ data cũ                                                             | Cân nhắc phạm vi yêu cầu của đồ án → chọn hướng (a) rewrite theo Chuyên đề 3                          |
| 2   | 2026-07-24 | [HOC]  | Cursor Agent | "Khám phá cấu trúc data xlsx mới" (câu hỏi phân tích, không yêu cầu sinh mã)                                                                                                                     | Mô tả: 1799 dòng × 32 cột, 6 quận, một loại hình, các trường`direction`/`furnishing`/`legal` lưu dạng mã số                                   | Tự đối chiếu với schema cũ, tự ghi nhận phạm vi thay đổi cần làm                                      |
| 3   | 2026-07-25 | [HOC]  | Cursor Agent | "Phân tích schema mới: những trường nào cần giữ nguyên, những trường dạng mã cần lưu ý gì khi mã hóa?"                                                                                           | Gợi ý:`PropertyListing` 19 trường, các mã (direction_code, balcony_code, furnishing_code, legal_code) nên giữ kiểu số nguyên kèm bảng mapping | Tự quyết định giữ mã số thay vì one-hot, nhằm hạn chế tăng số chiều; bộ test 9/9 đạt                  |
| 4   | 2026-07-26 | [CODE] | Cursor Agent | "Viết hàm`normalize_direction`, `decode_furnishing`, `decode_legal` theo mapping mình viết: 1..8 / 1..4 / 1,2,4,5,6"                                                                             | Hàm`normalize_direction` (decode 1..8), `decode_furnishing` (1..4), `decode_legal` (1,2,4,5,6)                                                | học viên cung cấp mapping, AI viết hàm; bộ test 9/9 đạt                                              |
| 5   | 2026-07-27 | [HOC]  | Cursor Agent | "Giải thích cho mình sự khác biệt giữa giá/m² và tổng giá khi chuẩn hóa; nên xử lý thế nào?"                                                                                                     | Giải thích: log-transform phù hợp với phân phối lệch phải của`price`; `price_per_m2` cần lọc ngoại lệ 3σ                                      | Cân nhắc thực nghiệm trên tập train → quyết định log-transform cho`price`, giữ raw cho `price_per_m2` |
| 6   | 2026-07-28 | [CODE] | Cursor Agent | "Update`src/data_manager.py` + `pipeline.py` để đọc được cả CSV và XLSX; `NUMERIC_COLS` gồm 9 cột (thêm direction_code, balcony_code, furnishing_code, legal_code, image_count, apartment_type)" | Hỗ trợ đọc CSV và XLSX;`NUMERIC_COLS` được cập nhật đúng 9 cột                                                                                | Pipeline chạy đến cuối                                                                                |
| 7   | 2026-07-29 | [CODE] | Cursor Agent | "Update`tests/` — 45 tests cho schema mới. Mình đã viết `test_plan.md`, viết mã theo plan đó"                                                                                                    | Sửa test_domain.py, test_cleaner.py, test_data_manager.py, test_features.py, test_recommender.py                                              | 45/45 đạt                                                                                             |
| 8   | 2026-07-30 | [CODE] | Cursor Agent | "Update`scripts/make_neighborhood_amenities.py` cho xlsx; giữ logic cũ, chỉ đổi đầu vào"                                                                                                         | Script đọc xlsx, sinh ra mapping amenities tương ứng 6 quận                                                                                   | Sinh ra 89 dòng, tỉ lệ đối sánh 99%                                                                   |
| 9   | 2026-07-31 | [HOC]  | Cursor Agent | "So sánh K-Means và K-Medoids cho dữ liệu BĐS có ngoại lệ; mình nên chọn thuật toán nào?"                                                                                                        | Giải thích: K-Medoids bền hơn với ngoại lệ nhưng tốn thời gian hơn; K-Means chấp nhận được nếu lọc ngoại lệ bằng IQR                          | Tự quyết định giữ K-Means, chọn K=4, giá trị silhouette 0.083                                         |
| 10  | 2026-08-01 | [CODE] | Cursor Agent | "Update 4 notebooks cho schema căn hộ theo outline mình viết (EDA / Cluster / Recommend / Visualize)"                                                                                            | 4 file`.ipynb` mới, các bước khớp outline                                                                                                     | Chạy qua`nbclient`, 4/4 chạy được đến cuối                                                            |
| 11  | 2026-08-02 | [HOC]  | Cursor Agent | "Giá trị R² của Random Forest chỉ ~0.169; con số này có ý nghĩa gì về mặt kỹ thuật và đặc thù ngành?"                                                                                            | Giải thích: giá BĐS phụ thuộc nhiều yếu tố vị trí/ngõ/hẻm không có trong tập dữ liệu → R² thấp phản ánh đúng đặc thù dữ liệu                  | Tự viết phần "Giới hạn mô hình" trong báo cáo dựa trên nhận định này                                  |
| 12  | 2026-08-03 | [CODE] | Cursor Agent | "Sửa 3 lỗi test nhỏ (encoding UTF-8 cho input tiếng Việt, một test count bị lệch). Mình đã paste traceback"                                                                                      | Sửa pytest fixture, thêm`encoding='utf-8'`                                                                                                    | 45/45 đạt                                                                                             |
| 13  | 2026-08-04 | [HOC]  | Cursor Agent | "Silhouette 0.083 có thấp quá không? ngưỡng nào thì chấp nhận được?"                                                                                                                             | Giải thích: 0.083 thấp nhưng chấp nhận được với dữ liệu BĐS (cụm chồng lấn); nên đối chiếu thêm Davies–Bouldin                                | Tự quyết định không thay đổi K, ghi nhận giới hạn trong báo cáo                                       |
| 14  | 2026-08-05 | [VIET] | Cursor Agent | "Gợi ý cấu trúc 4 mục cho`final_report.md` (theo đề cương giảng viên); mình tự viết nội dung"                                                                                                    | Outline 4 mục, gợi ý 3 ý chính mỗi mục                                                                                                        | học viên tự viết; AI chỉ gợi ý cách diễn đạt                                                         |
| 15  | 2026-08-06 | [HOC]  | Cursor Agent | "Coverage amenities 99% so với 67% của data cũ; giải thích vì sao có sự khác biệt?"                                                                                                              | Giải thích: do script xlsx đọc được 6 quận thay vì 24 quận, truy vấn OSM Overpass đối sánh cao hơn                                            | Tự viết phần "So sánh với data cũ" trong báo cáo                                                      |
| 16  | 2026-08-07 | [VIET] | Cursor Agent | "Cập nhật`README.md`, `data_dictionary.md`, `slide_outline.md`, `member_contributions.md` cho phù hợp với data mới"                                                                              | README.md, final_report.md, data_dictionary.md, slide_outline.md, member_contributions.md đã được rà lại                                      | học viên tự rà soát và sửa; AI chỉ gợi ý format                                                      |
| 17  | 2026-08-08 | [VIET] | Cursor Agent | "Rà lại toàn bộ file, kiểm tra lỗi chính tả và định dạng markdown — mình đã paste diff"                                                                                                          | Sửa 4 lỗi chính tả, làm gọn 2 bảng cho thống nhất                                                                                             | Commit phiên bản cuối                                                                                 |

## 4. Tổng hợp theo mức sử dụng

| Mức                        | Số lượt | Đặc điểm                                                                           |
| -------------------------- | ------- | ---------------------------------------------------------------------------------- |
| [HOC] Tự học / nghiên cứu  | 6       | Không sinh mã mới; AI chỉ trả lời câu hỏi phân tích, học viên tự đưa ra quyết định |
| [CODE] AI hỗ trợ lập trình | 7       | học viên chốt thiết kế / mapping / outline; AI dựng mã theo đặc tả                |
| [VIET] AI hỗ trợ viết      | 3       | học viên tự viết nội dung; AI gợi ý cấu trúc, sửa câu                             |
| **Tổng**                   | **17**  |                                                                                    |

## 5. Quy trình kiểm chứng và phản biện

Toàn bộ kết quả do AI hỗ trợ đều được kiểm chứng lại theo các bước sau:

1. **Kiểm thử tự động**: `pytest tests/ -v` — 45/45 đạt (sau khi sửa 3 lỗi test ban đầu liên quan encoding và test count).
2. **Pipeline đầu cuối**: `python3 -m src.pipeline` chạy đến cuối, sinh `metrics.json`, `sample_recommendations.csv` và 12 hình.
3. **Notebook**: dùng `nbclient.NotebookClient.execute()` cho 4 notebook, không phát sinh lỗi.
4. **Kết quả đầu ra**:
   - R² của Random Forest ≈ 0.169 (mô hình có kết quả tốt nhất trên tập kiểm tra).
   - Baseline Dummy R² ≈ -0.041 (âm — phù hợp với mô hình nền không học).
   - K-Means: K=4, silhouette 0.083 (thấp — phản ánh các cụm chồng lấn, phù hợp với đặc thù BĐS).
   - Tỉ lệ phủ amenities: 1763/1779 ≈ 99% (so với 67% của data cũ).
5. **Giải trình được từng quyết định**: lý do log-transform, lý do chọn feature, lý do lọc tolerance 20%, lý do schema mới cần thêm mã số.

## 6. Hạn chế và những điểm học viên tự chịu trách nhiệm

Những nội dung dưới đây được học viên tự thực hiện, không thông qua AI:

- **Chọn thuật toán cuối**: K-Means (K=4), Random Forest — dựa trên đọc tài liệu scikit-learn và quan sát giá trị silhouette.
- **Phân tích bối cảnh kết quả**: chỉ mô tả dựa trên số liệu, không nhờ AI diễn giải.
- **Nhận xét học thuật về giới hạn mô hình**: dựa trên quan sát thực nghiệm (R²=0.169, silhouette=0.083) và tài liệu đã đọc.
- **Bảng mapping `direction_code` / `furnishing_code` / `legal_code`**: tự tra từ data dictionary và tự viết.
- **Outline các phần báo cáo**: dựa trên đề cương giảng viên cung cấp, học viên tự phân chia mục.

## 7. Một số nhận định học thuật do học viên tự viết

- Phân phối giá/m² lệch phải là lý do áp dụng log-transform; raw `price_per_m2` được giữ để đọc trực tiếp trong phần EDA.
- Silhouette thấp phản ánh đặc thù BĐS: vị trí cụ thể (ngõ/hẻm, tầng, hướng chi tiết) không có trong tập dữ liệu, nên các cụm dễ chồng lấn.
- R² ~0.17 là giới hạn cố hữu khi không có thông tin vị trí chính xác (lat/lon chi tiết); mô hình không được kỳ vọng cao hơn trên tập dữ liệu hiện tại.
- Giữ mã số (direction_code, ...) thay vì one-hot nhằm hạn chế tăng số chiều và giữ khả năng tra cứu ngược.
- Lọc giá 3σ nhằm loại tin rao ảo hoặc lỗi nhập; phân phối còn lại gần chuẩn hơn, phù hợp với các mô hình giả định tuyến tính.

## 8. Tự đánh giá

Trong quá trình làm đồ án, học viên nhận thấy việc sử dụng AI ở mức [HOC] mang lại hiệu quả rõ nhất, đặc biệt với các câu hỏi về lý thuyết và đặc thù dữ liệu. Ở mức [CODE], AI chỉ phát huy tác dụng khi học viên đã có đặc tả rõ; các trường hợp đặc tả mơ hồ thường phải chỉnh sửa nhiều lần. Một số hạn chế còn tồn tại: bộ test chưa bao phủ trường hợp ngoại lệ phức tạp (giá cực trị, mã ngoài tập mapping), và phần phân tích giới hạn mô hình có thể sâu hơn nếu có thêm thời gian.
