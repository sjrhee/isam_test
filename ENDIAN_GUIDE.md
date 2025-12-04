# C-ISAM 파일의 엔디안(Endian) 이해 가이드

## 📌 빠른 답변

**Q: HP-UX의 리틀엔디안 경우 데이터 구조 파악이 어려울 수 있나?**

**A: 어렵지 않습니다!** ✓
- 파일 구조는 동일합니다
- 정수 필드의 바이트 순서만 다릅니다
- 자동 엔디안 감지로 완전히 해결 가능합니다

---

## 1. 엔디안의 기본 개념

### 엔디안(Endian)이란?

멀티바이트 정수를 메모리에 저장하는 방식입니다.

**예시: 정수 0x12345678을 4바이트로 저장**

```
빅엔디안 (Big-Endian):
  메모리 주소 0: 0x12 (MSB - Most Significant Byte)
  메모리 주소 1: 0x34
  메모리 주소 2: 0x56
  메모리 주소 3: 0x78 (LSB - Least Significant Byte)

리틀엔디안 (Little-Endian):
  메모리 주소 0: 0x78 (LSB)
  메모리 주소 1: 0x56
  메모리 주소 2: 0x34
  메모리 주소 3: 0x12 (MSB)
```

### 주요 시스템의 엔디안

#### 빅엔디안 (Big-Endian) 계열
- **IBM POWER (AIX)** - PowerPC 기반
- **Sun SPARC (Solaris)**
- **Motorola 68000**
- **HP-UX on PA-RISC** - HP-UX 초기 버전
- **MIPS** (일부)

#### 리틀엔디안 (Little-Endian) 계열
- **Intel x86/x86-64** - 현재 PC, 서버
- **ARM** - 모바일, 임베디드
- **VAX** - 레거시
- **HP-UX on Itanium** - 현대 HP-UX

#### HP-UX의 엔디안 변화

```
HP-UX 버전별:
├─ PA-RISC 기반 (1990년대-2000년대 초)
│  ├─ PA-RISC 1.0/1.1 (32-bit) → 빅엔디안
│  └─ PA-RISC 2.0 (64-bit) → 빅엔디안
│
└─ Itanium 기반 (2000년대 후반-현재)
   ├─ HP Integrity (Itanium) → 리틀엔디안
   └─ Superdome → 리틀엔디안
```

---

## 2. 실제 예시 비교

### Big-Endian (우리 시스템)

```
파일 내용 (hex): 00 00 00 01 43 75 73 74 6f 6d 65 72 ...
                └─ ID ─┘   └──────── Name ────────┘

Python 읽기:
  struct.unpack('>I', b'\x00\x00\x00\x01') → 1 ✓
```

### Little-Endian (HP-UX Itanium)

```
파일 내용 (hex): 01 00 00 00 43 75 73 74 6f 6d 65 72 ...
                └─ ID ─┘   └──────── Name ────────┘

Python 읽기 (리틀엔디안):
  struct.unpack('<I', b'\x01\x00\x00\x00') → 1 ✓

Python 읽기 (빅엔디안으로 잘못 읽음):
  struct.unpack('>I', b'\x01\x00\x00\x00') → 16843009 ✗
```

---

## 3. ISAM 파일 분석에 미치는 영향

### 영향을 받는 필드 타입

| 필드 타입 | 엔디안 영향 | 해결 방법 |
|----------|-----------|---------|
| `int`, `long` | ✗ **영향 있음** | `struct.unpack('<I')` 또는 `struct.unpack('>I')` |
| `float`, `double` | ✗ **영향 있음** | 해당 엔디안 형식 사용 |
| `char[]` (문자열) | ✓ **영향 없음** | 직접 읽으면 됨 |
| `\r\n` (구분자) | ✓ **영향 없음** | 엔디안 무관 |

### 영향을 받지 않는 부분

```
✓ 파일 구조
  - 레코드 크기: 186 바이트
  - 레코드 개수: 1000개
  - 필드 오프셋: 동일

✓ 문자열 필드
  - Name, Email, Phone, Date
  - 각 바이트가 독립적이므로 순서 무관

✓ 파일 분석
  - 레코드 경계 감지
  - 필드 구조 파악
```

---

## 4. 자동 엔디안 감지 방법

### 원리

ID 필드(첫 4바이트)를 Big-Endian과 Little-Endian으로 모두 읽어서,
어느 것이 합리적인 범위(1~999999)인지 판단합니다.

### 코드 예시

```python
import struct

def detect_endian(first_record):
    """첫 레코드로부터 엔디안 자동 감지"""
    
    # Big-Endian으로 읽기
    be_value = struct.unpack('>I', first_record[0:4])[0]
    
    # Little-Endian으로 읽기
    le_value = struct.unpack('<I', first_record[0:4])[0]
    
    # ID가 1-999999 범위일 가능성으로 판단
    if 1 <= be_value <= 999999:
        return '>'  # Big-Endian
    elif 1 <= le_value <= 999999:
        return '<'  # Little-Endian
    else:
        return '>'  # 기본값

# 사용 예
record = ...  # DAT 파일의 첫 레코드
endian = detect_endian(record)
id_value = struct.unpack(f'{endian}I', record[0:4])[0]
```

---

## 5. analyze_isam.py 사용법

### 자동 엔디안 감지 (권장)

```bash
python3 analyze_isam.py customers.isam.dat customers.isam.idx
```

**출력:**
```
감지된 엔디안: Big-Endian (빅엔디안)
  (정수 필드 해석에 사용됨)
```

### Big-Endian 강제 설정

```bash
python3 analyze_isam.py --endian big customers.isam.dat customers.isam.idx
```

### Little-Endian 강제 설정

```bash
python3 analyze_isam.py --endian little customers.isam.dat customers.isam.idx
```

---

## 6. C 코드에서의 엔디안 처리

### Big-Endian에서 데이터 읽기 (PA-RISC)

```c
#include <isam.h>

struct customer {
    int id;           // Big-Endian 정수
    char name[50];
    char email[100];
    char phone[20];
    char date[11];
};

void read_record() {
    struct customer rec;
    isread(fd, (char *)&rec, ISNEXT);
    
    // id는 ISAM이 자동으로 Big-Endian으로 저장했으므로
    // 그대로 사용 가능
    printf("ID: %d\n", rec.id);  // 정상 작동
}
```

### Little-Endian에서 데이터 읽기 (Itanium)

```c
// 방법 1: ISAM이 자동으로 처리 (권장)
// ISAM은 각 시스템의 네이티브 엔디안으로 자동 변환
struct customer rec;
isread(fd, (char *)&rec, ISNEXT);
printf("ID: %d\n", rec.id);  // 자동으로 올바르게 읽혀짐

// 방법 2: 수동 변환 필요시
#include <netinet/in.h>  // ntohl, htonl

int id_value = ntohl(rec.id);  // Little-Endian → Big-Endian으로 변환
```

---

## 7. 파일 마이그레이션

### Big-Endian 파일을 Little-Endian으로 변환

```python
import struct

def convert_endian(input_file, output_file, record_size):
    """Big-Endian DAT 파일을 Little-Endian으로 변환"""
    
    with open(input_file, 'rb') as f_in, open(output_file, 'wb') as f_out:
        while True:
            record = f_in.read(record_size)
            if not record:
                break
            
            # ID 필드 (첫 4바이트) 변환
            id_be = struct.unpack('>I', record[0:4])[0]
            id_le = struct.pack('<I', id_be)
            
            # 변환된 ID + 나머지 데이터
            f_out.write(id_le + record[4:])

# 사용
convert_endian('customers_be.isam.dat', 
               'customers_le.isam.dat', 
               186)
```

---

## 8. 실전 시나리오

### 시나리오 1: 미지의 ISAM 파일 분석

```bash
# 1단계: 파일 크기 확인
ls -lh *.isam.dat

# 2단계: 첫 몇 바이트 확인
hexdump -C *.isam.dat | head

# 3단계: 자동 엔디안 감지 및 분석
python3 analyze_isam.py *.isam.dat *.isam.idx

# 결과: 파일 구조 완전히 파악됨
```

### 시나리오 2: PA-RISC에서 Itanium으로 마이그레이션

```bash
# 1단계: PA-RISC (Big-Endian)에서 ISAM 파일 생성
./load_customers customers.csv customers.isam

# 2단계: 파일 전송
scp customers.isam.* user@itanium_server:/tmp/

# 3단계: Itanium (Little-Endian)에서 엔디안 변환
python3 convert_endian.py customers.isam.dat \
                         customers_converted.isam.dat 186

# 4단계: 변환된 파일에서 데이터 읽기
./read_customers customers_converted.isam
```

### 시나리오 3: 여러 파일 일괄 분석

```bash
for f in *.isam.dat; do
    idx="${f%.dat}.idx"
    echo "=== $f 분석 ==="
    python3 analyze_isam.py "$f" "$idx"
    echo ""
done
```

---

## 9. 디버깅 팁

### 문제: ID가 이상한 값으로 읽힘

```
예상: ID = 1
실제: ID = 16843009

→ 엔디안 설정 확인!
  python3 analyze_isam.py --endian little file.dat file.idx
```

### 문제: 문자열이 깨짐

```
예상: "Customer_0001"
실제: 문자열 정상인데 필드가 잘못 오프셋

→ 레코드 크기 확인!
  파일크기 ÷ 예상 레코드 수 = 올바른 레코드 크기?
```

### 문제: 레코드 경계를 못 찾음

```
→ 구분자 확인!
  hexdump -C file.dat | grep "0d 0a"
  
  0d 0a = \r\n (올바름)
  00 00 = 다른 형식일 가능성
```

---

## 10. 결론 및 권장사항

### ✅ 최종 답변

| 질문 | 답변 |
|------|------|
| 리틀엔디안도 파악 가능한가? | ✓ 예, 완벽히 가능 |
| 추가 작업이 필요한가? | ✓ 엔디안만 감지하면 됨 |
| 복잡도는? | ✓ 매우 간단 (1글자 차이) |
| 자동화 가능한가? | ✓ 완전 자동 감지 가능 |

### 🎯 권장 사항

1. **항상 자동 엔디안 감지 사용**
   ```bash
   python3 analyze_isam.py --endian auto file.dat file.idx
   ```

2. **모든 ISAM 도구에 엔디안 옵션 추가**
   ```
   load_customers.c → --endian 옵션
   read_customers.c → --endian 옵션
   ```

3. **크로스 플랫폼 호환성**
   - PA-RISC (Big) ↔ Itanium (Little)
   - Linux (Big/Little) ↔ Windows (Little)
   - 모두 자동 감지로 처리 가능

---

## 참고 자료

### 엔디안 확인 명령어

```bash
# 시스템의 엔디안 확인
lscpu | grep -i "byte order"

# 또는
python3 -c "import sys; print(sys.byteorder)"
```

### 관련 ISAM 함수

```c
// stlong() - 정수를 저장 (자동으로 시스템 엔디안 사용)
stlong(value, buffer);

// ldlong() - 정수를 로드 (자동으로 시스템 엔디안 사용)
int value = ldlong(buffer);
```

ISAM 라이브러리 자체가 각 시스템의 엔디안을 자동으로 처리하므로,
C 코드에서는 대부분 투명하게 작동합니다!

---

**작성일**: 2024년 12월
**최종 업데이트**: analyze_isam.py v2.0 (엔디안 자동 감지)
