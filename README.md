# C-ISAM 분석 및 개발 사전 테스트

IBM Informix C-ISAM (Indexed Sequential Access Method) 데이터베이스 파일 구조 분석 및 관리 도구입니다.

## 📋 사전 테스트 개요

이 사전 테스트는 C-ISAM 파일의 구조를 파악하고, 데이터를 로드/읽기하는 완전한 시스템을 제공합니다.

### 주요 기능

- **자동 ISAM 파일 분석**: `.dat`와 `.idx` 파일로부터 테이블 구조 역공학
- **엔디안 자동 감지**: Big-Endian과 Little-Endian 시스템 모두 지원
- **CSV → ISAM 변환**: CSV 파일을 C-ISAM 형식으로 로드
- **ISAM → CSV 추출**: ISAM 파일에서 데이터 읽기
- **크로스 플랫폼 호환**: PA-RISC, Itanium, Linux, Windows 지원

---

## 📁 파일 구조

```
.
├── README.md                      # 이 파일
├── .gitignore                     # Git 제외 설정
│
├── 📊 핵심 도구
│   ├── analyze_isam.py           # ISAM 파일 자동 분석 (v2.0)
│   ├── load_customers.c          # CSV → ISAM 로더
│   ├── read_customers.c          # ISAM 데이터 읽기
│   └── generate_customer_csv.py   # 테스트 CSV 생성
│
├── 📚 문서
│   ├── ISAM_ANALYSIS_GUIDE.md    # 기본 개념 및 분석 방법
│   └── ENDIAN_GUIDE.md           # 엔디안 상세 가이드
│
└── 📊 테스트 데이터
    └── customers.csv             # 1000 레코드 샘플 데이터
```

---

## 🚀 빠른 시작

### 1. 테스트 데이터 생성

```bash
python3 generate_customer_csv.py
# → customers.csv 생성 (1000 레코드)
```

### 2. ISAM 파일 로드

```bash
gcc load_customers.c -I/usr/include -L/usr/lib -lisam -o load_customers.out
./load_customers.out customers.csv customers.isam
# → customers.isam.dat, customers.isam.idx 생성
```

### 3. ISAM 파일 분석

```bash
python3 analyze_isam.py customers.isam.dat customers.isam.idx
```

**자동 엔디안 감지 출력:**
```
감지된 엔디안: Big-Endian (빅엔디안)
  (정수 필드 해석에 사용됨)

DAT 파일 분석
파일 크기: 186,368 바이트
레코드 크기: 186 바이트
레코드 개수: 1,000

첫 3개 레코드 분석:
[레코드 1]
  ID: 1
  Name: "Customer_0001"
  Email: "customer1@example.com"
  Phone: "010-2637-3125"
  Date: "2025-03-31"
```

### 4. ISAM 데이터 읽기

```bash
gcc read_customers.c -I/usr/include -L/usr/lib -lisam -o read_customers.out
./read_customers.out customers.isam
# → 데이터 검증 및 샘플 레코드 표시
```

---

## 🔧 analyze_isam.py 사용법

### 자동 엔디안 감지 (권장)

```bash
python3 analyze_isam.py file.dat file.idx
```

### Big-Endian 강제 설정

```bash
python3 analyze_isam.py --endian big file.dat file.idx
```

### Little-Endian 강제 설정

```bash
python3 analyze_isam.py --endian little file.dat file.idx
```

### 옵션

```
--endian big      Big-Endian 강제
--endian little   Little-Endian 강제
--endian auto     자동 감지 (기본값)
```

---

## 📊 지원 플랫폼

| 플랫폼 | 아키텍처 | 엔디안 | 상태 |
|------|--------|-------|------|
| HP-UX | PA-RISC | Big-Endian | ✅ 지원 |
| HP-UX | Itanium | Little-Endian | ✅ 지원 |
| AIX | POWER | Big-Endian | ✅ 지원 |
| Solaris | SPARC | Big-Endian | ✅ 지원 |
| Linux | x86/x86-64 | Little-Endian | ✅ 지원 |
| Windows | x86-64 | Little-Endian | ✅ 지원 |

---

## 📋 ISAM 파일 구조

### 데이터 파일 (.dat)

```
[레코드 1]
├─ ID (4 바이트, Big-Endian): 00 00 00 01
├─ Name (50 바이트, ASCII): "Customer_0001          "
├─ Email (100 바이트, ASCII): "customer1@example.com..."
├─ Phone (20 바이트, ASCII): "010-2637-3125      "
├─ Date (11 바이트, ASCII): "2025-03-31  "
└─ 구분자 (2 바이트): 0d 0a (\r\n)
   [총 186 바이트]

[레코드 2]
├─ ...
[더 많은 레코드]
```

### 인덱스 파일 (.idx)

```
[헤더]
├─ 매직 넘버: 0xfe53
├─ 버전: 0x02
├─ 키 오프셋: 0 (ID 필드)
├─ 키 길이: 4 바이트
├─ 키 타입: 3 (LONGTYPE)
└─ 플래그: 0xff (ISDUPS - 중복 허용)

[인덱스 데이터]
├─ 1 → 레코드 1 위치
├─ 2 → 레코드 2 위치
├─ ...
└─ 1000 → 레코드 1000 위치
```

---

## 🔑 핵심 개념

### C-ISAM (Indexed Sequential Access Method)

- **레거시 데이터베이스**: IBM Informix가 개발한 고성능 파일 기반 DB
- **인덱싱**: B-tree 기반 인덱스로 빠른 검색
- **순차 접근**: 레코드를 순서대로 스캔 가능
- **고정 길이 레코드**: 각 레코드가 동일한 크기

### 엔디안 (Endian)

**Big-Endian** (PA-RISC, SPARC, AIX)
- 가장 중요한 바이트가 먼저 저장
- 정수 1: `00 00 00 01`

**Little-Endian** (Itanium, x86/x86-64, ARM)
- 가장 중요하지 않은 바이트가 먼저 저장
- 정수 1: `01 00 00 00`

**자동 감지**: `analyze_isam.py`가 첫 레코드를 분석하여 자동으로 감지

---

## 📚 상세 문서

### [ISAM_ANALYSIS_GUIDE.md](./ISAM_ANALYSIS_GUIDE.md)
- ISAM 파일 구조의 기본 개념
- 단계별 분석 방법
- 헥스덤프를 이용한 수동 분석
- Python을 이용한 자동 분석

### [ENDIAN_GUIDE.md](./ENDIAN_GUIDE.md)
- 엔디안의 기본 개념
- Big-Endian vs Little-Endian 비교
- HP-UX 버전별 엔디안 정보
- C 코드에서의 엔디안 처리
- 파일 마이그레이션 방법
- 실전 시나리오 10가지

---

## 💻 C 코드 컴파일

### 컴파일 명령어

```bash
# 로더 컴파일
gcc load_customers.c -I/usr/include -L/usr/lib -lisam -o load_customers.out

# 리더 컴파일
gcc read_customers.c -I/usr/include -L/usr/lib -lisam -o read_customers.out
```

### 실행 예시

```bash
# CSV에서 ISAM으로 로드
./load_customers.out customers.csv customers.isam
# → Total records loaded: 1000, Errors: 0

# ISAM 데이터 읽기
./read_customers.out customers.isam
# → 첫 20개 레코드 출력
```

---

## 🐍 Python 스크립트

### analyze_isam.py

ISAM 파일의 구조를 자동으로 분석하고 C 구조체 정의를 생성합니다.

**기능:**
- 자동 엔디안 감지
- 레코드 구조 분석
- 필드 오프셋 계산
- C 구조체 코드 생성
- Python 언팩 코드 생성

**사용법:**
```bash
python3 analyze_isam.py [--endian {big|little|auto}] <dat_file> <idx_file>
```

### generate_customer_csv.py

테스트용 고객 데이터 CSV 파일을 생성합니다.

**생성 데이터:**
- 1000 레코드
- 5 컬럼: customer_id, name, email, phone, registration_date
- 랜덤 데이터 포함

---

## 🔄 워크플로우 예시

### 워크플로우 1: 데이터 로드 및 검증

```bash
# 1. 테스트 CSV 생성
python3 generate_customer_csv.py

# 2. 컴파일
gcc load_customers.c -I/usr/include -L/usr/lib -lisam -o load_customers.out

# 3. ISAM으로 로드
./load_customers.out customers.csv customers.isam

# 4. 구조 분석
python3 analyze_isam.py customers.isam.dat customers.isam.idx

# 5. 데이터 검증
gcc read_customers.c -I/usr/include -L/usr/lib -lisam -o read_customers.out
./read_customers.out customers.isam
```

### 워크플로우 2: 다른 시스템에서 파일 분석

```bash
# 미지의 ISAM 파일이 있는 경우

# 1. 파일 크기 확인
ls -lh *.isam.*

# 2. 구조 자동 분석
python3 analyze_isam.py file.isam.dat file.isam.idx
# → 자동으로 Big/Little-Endian 감지

# 3. 엔디안 확인 가능
python3 analyze_isam.py --endian big file.isam.dat file.isam.idx
```

---

## 🛠️ 문제 해결

### 컴파일 오류: "cannot find -lisam"

```bash
# 해결: ISAM 라이브러리 경로 확인
find / -name "libisam*" 2>/dev/null

# 올바른 경로로 컴파일
gcc load_customers.c -I/path/to/include -L/path/to/lib -lisam -o load_customers.out
```

### ID 값이 이상한 경우

```bash
# 엔디안 확인
python3 analyze_isam.py --endian little file.dat file.idx
```

### 파일을 다른 시스템으로 이동

```bash
# Big-Endian에서 Little-Endian으로 변환 스크립트 필요
# ENDIAN_GUIDE.md 참고
```

---

## 📝 라이센스

이 사전 테스트는 교육 및 레거시 시스템 마이그레이션 목적으로 제공됩니다.

---

## 🤝 기여

버그 리포트, 기능 요청, 개선 사항은 이슈를 통해 제시해주세요.

---

## 📞 문의

C-ISAM 파일 분석 및 마이그레이션과 관련된 질문이 있으면 이슈를 생성해주세요.

---

## 📚 참고 자료

- [ISAM_ANALYSIS_GUIDE.md](./ISAM_ANALYSIS_GUIDE.md) - 기본 개념
- [ENDIAN_GUIDE.md](./ENDIAN_GUIDE.md) - 엔디안 상세 가이드

---

**마지막 업데이트**: 2024년 12월 4일
**버전**: 2.0 (엔디안 자동 감지 완전 지원)
