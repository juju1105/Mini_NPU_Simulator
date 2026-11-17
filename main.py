
import time
import json


# 1. JSON 데이터 불러오기
def load_data():
    try:
        with open("data.json", "r", encoding="utf-8") as file:
            data = json.load(file)

        print("\nJSON 데이터 불러오기 성공!")
        return data

    except FileNotFoundError:
        print("오류: data.json 파일을 찾을 수 없습니다.")
        return None

    except json.JSONDecodeError:
        print("오류: JSON 파일 형식이 올바르지 않습니다.")
        return None


# 2. 정답 라벨 통일
def normalize_label(label):
    label = str(label).strip().lower()

    if label in ["+", "cross"]:
        return "Cross"

    elif label == "x":
        return "X"

    return "UNDECIDED"


# 3. 행렬 크기 검증
def is_valid_matrix(matrix, size):
    if not isinstance(matrix, list) or len(matrix) != size:
        return False

    for row in matrix:
        if not isinstance(row, list) or len(row) != size:
            return False

        for value in row:
            if not isinstance(value, (int, float)):
                return False

    return True


# 4. MAC 연산
def mac_operation(pattern, filter_data):
    score = 0.0
    n = len(pattern)

    for i in range(n):
        for j in range(n):
            score += pattern[i][j] * filter_data[i][j]

    return score


# 5. 패턴 판정
def classify_pattern(pattern, filter_a, filter_b):
    epsilon = 1e-9

    score_a = mac_operation(pattern, filter_a)
    score_b = mac_operation(pattern, filter_b)

    if abs(score_a - score_b) <= epsilon:
        result = "UNDECIDED"
    elif score_a > score_b:
        result = "A"
    else:
        result = "B"

    return score_a, score_b, result


# 6. 연산 시간 측정
def measure_mac_time(pattern, filter_a, filter_b, repeats=10):
    start_time = time.perf_counter()

    for _ in range(repeats):
        mac_operation(pattern, filter_a)
        mac_operation(pattern, filter_b)

    end_time = time.perf_counter()

    total_time = end_time - start_time
    average_time = (total_time / repeats) * 1000

    return average_time


# 7. JSON 패턴 분석
def run_json_mode(data):
    total = 0
    passed = 0
    failed = 0
    failures = []

    print("\n=== JSON 패턴 분석 시작 ===")

    for size in [5, 13, 25]:
        size_key = f"size_{size}"

        print(f"\n--- {size}x{size} 패턴 분석 ---")

        filters = data["filters"].get(size_key)

        if not filters:
            print(f"오류: {size_key} 필터를 찾을 수 없습니다.")
            continue

        cross_filter = filters.get("cross")
        x_filter = filters.get("x")

        if not is_valid_matrix(cross_filter, size):
            print("오류: Cross 필터의 크기가 올바르지 않습니다.")
            continue

        if not is_valid_matrix(x_filter, size):
            print("오류: X 필터의 크기가 올바르지 않습니다.")
            continue

        for pattern_name, pattern_data in data["patterns"].items():

            if not pattern_name.startswith(size_key):
                continue

            total += 1

            pattern = pattern_data.get("input")
            expected = normalize_label(pattern_data.get("expected"))

            # 패턴 크기 검증
            if not is_valid_matrix(pattern, size):
                failed += 1

                failures.append({
                    "pattern": pattern_name,
                    "reason": "패턴 크기 오류"
                })

                print(f"{pattern_name}: FAIL - 패턴 크기 오류")
                continue

            # MAC 점수 계산
            cross_score = mac_operation(pattern, cross_filter)
            x_score = mac_operation(pattern, x_filter)

            # 결과 판정
            if abs(cross_score - x_score) <= 1e-9:
                result = "UNDECIDED"
            elif cross_score > x_score:
                result = "Cross"
            else:
                result = "X"

            # 정답 비교
            if result == expected:
                passed += 1
                status = "PASS"

            else:
                failed += 1
                status = "FAIL"

                failures.append({
                    "pattern": pattern_name,
                    "reason": (
                        f"예상 결과({expected})와 "
                        f"실제 결과({result}) 불일치"
                    )
                })

            print(f"\n패턴: {pattern_name}")
            print(f"Cross 점수: {cross_score}")
            print(f"X 점수: {x_score}")
            print(f"예상 결과: {expected}")
            print(f"실제 결과: {result}")
            print(f"판정: {status}")

    # 전체 분석 결과
    print("\n=== 전체 분석 결과 ===")
    print(f"전체 패턴: {total}")
    print(f"PASS: {passed}")
    print(f"FAIL: {failed}")

    # 실패 사례 분석
    print("\n=== 실패 사례 분석 ===")

    if failures:
        for item in failures:
            print(f"패턴: {item['pattern']}")
            print(f"실패 이유: {item['reason']}")
    else:
        print("실패한 패턴이 없습니다.")


# 8. MAC 성능 분석
def run_performance_test(data, repeats=10):
    print("\n=== MAC 성능 분석 ===")

    for size in [3, 5, 13, 25]:

        print(f"\n--- {size}x{size} 성능 측정 ---")

        if size == 3:
            pattern = [
                [1 for _ in range(size)]
                for _ in range(size)
            ]

            filter_a = [
                [1 for _ in range(size)]
                for _ in range(size)
            ]

            filter_b = [
                [0 for _ in range(size)]
                for _ in range(size)
            ]

        else:
            size_key = f"size_{size}"
            filters = data["filters"].get(size_key)

            if not filters:
                print("필터 데이터를 찾을 수 없습니다.")
                continue

            filter_a = filters["cross"]
            filter_b = filters["x"]

            pattern_data = next(
                (
                    item for name, item in data["patterns"].items()
                    if name.startswith(size_key)
                ),
                None
            )

            if pattern_data is None:
                print("패턴 데이터를 찾을 수 없습니다.")
                continue

            pattern = pattern_data["input"]

        average_time = measure_mac_time(
            pattern, filter_a, filter_b, repeats
        )

        operations = size * size

        print(f"반복 횟수: {repeats}회")
        print(f"MAC 연산량: {operations}회")
        print(f"평균 실행 시간: {average_time:.6f} ms")


# 9. 사용자 입력 행렬
def input_matrix(name, n):
    print(f"\n{name} 입력 ({n}줄, 각 줄에 숫자 {n}개)")

    matrix = []

    while len(matrix) < n:
        try:
            row = input(
                f"{len(matrix) + 1}번째 줄: "
            ).split()

            if len(row) != n:
                print(f"입력 형식 오류: 숫자 {n}개를 입력하세요.")
                continue

            row = [float(value) for value in row]
            matrix.append(row)

        except ValueError:
            print("입력 오류: 숫자만 입력하세요.")

    return matrix


# 10. 사용자 입력 모드
def user_input_mode():
    print("\n=== 사용자 입력 모드 ===")

    filter_a = input_matrix("필터 A", 3)
    filter_b = input_matrix("필터 B", 3)

    print("\n필터 입력이 완료되었습니다.")

    pattern = input_matrix("패턴", 3)

    score_a, score_b, result = classify_pattern(
        pattern,
        filter_a,
        filter_b
    )

    average_time = measure_mac_time(
        pattern,
        filter_a,
        filter_b
    )

    print("\n=== MAC 결과 ===")
    print("A 점수:", score_a)
    print("B 점수:", score_b)
    print("판정:", result)
    print(f"연산 시간(평균/10회): {average_time:.6f} ms")


# 11. 프로그램 실행
if __name__ == "__main__":
    data = load_data()

    if data:
        run_json_mode(data)
        run_performance_test(data)
