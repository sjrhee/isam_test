# C-ISAM 소스 코드 문서

## 개요
이 프로젝트는 **C-ISAM (Indexed Sequential Access Method)**을 사용하는 직원 관리 시스템입니다.  
IBM의 인덱스 순차 접근 방식을 활용하여 직원 데이터와 성과 기록을 관리합니다.

---

## 각 소스 파일 설명

### 1. `bld_file.c` - 파일 시스템 빌드
**목적**: 데이터베이스 파일 구조 초기화  
**기능**:
- 직원(employee) 파일 생성
- 성과(performance) 파일 생성
- 기본 인덱스 키 설정 (직원 번호 기반)
- ISAM 파일 시스템 구축

**실행 순서**: **1번째** (가장 먼저 실행)

---

### 2. `add_indx.c` - 2차 인덱스 추가
**목적**: 보조 인덱스 생성  
**기능**:
- 직원 파일의 성(Last Name) 필드에 인덱스 추가
- 성과 파일의 급여(Salary) 필드에 인덱스 추가
- 빠른 검색을 위한 보조 인덱스 구성

**실행 순서**: **2번째** (bld_file 이후)

---

### 3. `add_rcrd.c` - 레코드 추가
**목적**: 새로운 직원 및 성과 기록 입력  
**기능**:
- 새로운 직원 정보를 직원 파일에 추가
- 해당 직원의 첫 번째 성과 기록을 성과 파일에 추가
- 대화형으로 사용자 입력 받음
- 직원 번호, 이름 등의 데이터 입력

**실행 순서**: **3번째**

---

### 4. `upd_file.c` - 레코드 수정/삭제
**목적**: 직원 정보 수정 및 삭제  
**기능**:
- 기존 직원 기록 수정
- 직원 삭제 시 관련된 모든 성과 기록도 함께 삭제
- 삭제 옵션과 수정 옵션 제공
- 참조 무결성 유지 (직원 삭제 시 자동으로 성과 기록 정리)

**실행 순서**: **4번째 이후**

---

### 5. `sqntl_rd.c` - 순차 읽기
**목적**: 직원 정보 조회  
**기능**:
- 직원 번호 순으로 직원 파일 순차 읽기
- 모든 직원 레코드를 화면에 출력
- 직원 번호, 이름, 급여 등 정보 표시
- 전체 직원 목록 조회 용도

**실행 순서**: **조회용** (언제든 실행 가능)

---

### 6. `chaining.c` - 성과 기록 추가
**목적**: 직원의 성과 정보 입력  
**기능**:
- 직원의 성과 기록을 성과 파일에 추가
- 성과 등급에 따른 급여 인상 계산
  - A 등급: 6% 인상
  - B 등급: 4% 인상
  - C 등급: 2% 인상
- 기존 성과 정보와 새로운 정보 비교
- 급여 변동 추적

**실행 순서**: **5번째 이후**

---

### 7. `transctn.c` - 트랜잭션 기반 추가 (로그 파일 포함)
**목적**: 안정적인 직원 및 성과 정보 추가  
**기능**:
- 직원 및 성과 정보 추가 (add_rcrd와 유사)
- 트랜잭션 로깅 지원
- 복구 로그 파일(recovery.log) 생성
- 예기치 않은 오류 발생 시 데이터 복구 가능
- 데이터 무결성 보장

**실행 순서**: **6번째 이후** (프로덕션 환경 권장)

---

## 데이터 구조

### 직원(Employee) 파일
- **레코드 크기**: 84바이트
- **주요 필드**:
  - 직원 번호: 4바이트 (long 타입)
  - 성(Last Name): 20바이트
  - 기타 정보: 60바이트

### 성과(Performance) 파일
- **레코드 크기**: 50바이트
- **주요 필드**:
  - 직원 번호: 4바이트
  - 성과 등급: 6바이트
  - 급여: 포함

---

## 사용 순서

```
1. bld_file       → 파일 시스템 초기화
   ↓
2. add_indx       → 검색 인덱스 추가
   ↓
3. add_rcrd       → 첫 직원 데이터 입력
   ↓
4. sqntl_rd       → 입력된 데이터 확인 (필요시)
   ↓
5. chaining       → 성과 정보 추가
   ↓
6. upd_file       → 데이터 수정/삭제
   ↓
7. transctn       → 트랜잭션 기반 작업
```

---

## 컴파일 및 실행

### 컴파일
```bash
make              # 모든 파일 컴파일
make clean        # 빌드 결과 삭제
make clean-obj    # 오브젝트 파일만 삭제
make rebuild      # 전체 재빌드
make help         # 도움말 표시
```

### 각 프로그램 실행
```bash
./demo/build/bld_file        # 파일 시스템 생성
./demo/build/add_indx        # 인덱스 추가
./demo/build/add_rcrd        # 레코드 추가
./demo/build/upd_file        # 레코드 수정/삭제
./demo/build/sqntl_rd        # 데이터 조회
./demo/build/chaining        # 성과 기록 추가
./demo/build/transctn        # 트랜잭션 작업
```

---

## 주요 ISAM 함수

### 파일 관리 함수
| 함수 | 설명 |
|------|------|
| `isbuild()` | 새로운 ISAM 파일 생성 (레코드 길이, 키 정보 지정) |
| `isopen()` | ISAM 파일 열기 (읽기/쓰기 모드 지정) |
| `isclose()` | ISAM 파일 닫기 및 리소스 해제 |
| `iserase()` | ISAM 파일 삭제 |
| `isrename()` | 파일 이름 변경 |
| `isflush()` | 메모리 버퍼를 디스크에 강제 기록 |

### 레코드 조회 함수
| 함수 | 설명 |
|------|------|
| `isread()` | 현재 위치에서 레코드 읽기 (ISFIRST, ISLAST, ISNEXT 등 모드 포함) |
| `isstart()` | 순차 읽기 시작 지점 설정 |

### 레코드 작성/수정/삭제 함수
| 함수 | 설명 |
|------|------|
| `iswrite()` | 새 레코드 추가 (write mode) |
| `isinsert()` | 새 레코드 삽입 |
| `isrewrite()` | 현재 위치의 레코드 수정 |
| `isupdate()` | 지정된 레코드 수정 |
| `isdelete()` | 주키를 기반으로 레코드 삭제 |
| `isdelcurr()` | 현재 위치의 레코드 삭제 |
| `isdelrec()` | 레코드 번호로 레코드 삭제 |
| `isrewcurr()` | 현재 위치의 레코드 재작성 |
| `isrewrec()` | 레코드 번호로 레코드 재작성 |
| `iswrcurr()` | 현재 위치에 레코드 작성 |

### 인덱스 관리 함수
| 함수 | 설명 |
|------|------|
| `isaddindex()` | 보조(2차) 인덱스 추가 |
| `isdelindex()` | 인덱스 삭제 |
| `iscluster()` | 클러스터 인덱스 생성 (성능 최적화) |

### 정보 조회 함수
| 함수 | 설명 |
|------|------|
| `iskeyinfo()` | 키 정보 조회 |
| `isindexinfo()` | 인덱스 정보 조회 |
| `isdictinfo()` | 파일 딕셔너리 정보 조회 |
| `isnlsversion()` | NLS(국제화) 버전 확인 |
| `isglsversion()` | GLS(글로벌 언어) 버전 확인 |

### 잠금 및 트랜잭션 함수
| 함수 | 설명 |
|------|------|
| `islock()` | 파일 잠금 |
| `isunlock()` | 파일 잠금 해제 |
| `isbegin()` | 트랜잭션 시작 |
| `iscommit()` | 트랜잭션 커밋 (변경 사항 확정) |
| `isrollback()` | 트랜잭션 롤백 (변경 사항 취소) |
| `isrelease()` | 파일 잠금 해제 |

### 로깅 및 복구 함수
| 함수 | 설명 |
|------|------|
| `islogopen()` | 로그 파일 열기 (트랜잭션 로깅) |
| `islogclose()` | 로그 파일 닫기 |
| `isaudit()` | 감시 추적(audit trail) 활성화/비활성화 |
| `isrecover()` | 손상된 파일 복구 |
| `iscleanup()` | 정리 및 최적화 |

### 기타 함수
| 함수 | 설명 |
|------|------|
| `issetunique()` | 고유 ID 설정 |
| `isuniqueid()` | 고유 ID 조회 |
| `islangchk()` | 언어 체크 활성화 |
| `isnolangchk()` | 언어 체크 비활성화 |
| `islanginfo()` | 현재 로케일(collation) 정보 조회 |

### 데이터 변환 함수 (Load/Store)
이 함수들은 바이너리 형식과 프로그램 변수 간의 변환을 담당합니다.

**Load 함수 (바이너리 → 변수)**
| 함수 | 설명 |
|------|------|
| `ldlong()` | ISAM 파일의 long 타입 데이터 읽기 |
| `ldint()` | int 타입 데이터 읽기 |
| `ldfloat()` | float 타입 데이터 읽기 |
| `lddbl()` | double 타입 데이터 읽기 |
| `lddecimal()` | 소수점 데이터 읽기 |
| `ldchar()` | 문자열 데이터 읽기 |
| `ldfltnull()` | NULL 가능한 float 읽기 |
| `lddblnull()` | NULL 가능한 double 읽기 |

**Store 함수 (변수 → 바이너리)**
| 함수 | 설명 |
|------|------|
| `stlong()` | long 타입 데이터 저장 |
| `stint()` | int 타입 데이터 저장 |
| `stfloat()` | float 타입 데이터 저장 |
| `stdbl()` | double 타입 데이터 저장 |
| `stdecimal()` | 소수점 데이터 저장 |
| `stchar()` | 문자열 데이터 저장 |
| `stfltnull()` | NULL 가능한 float 저장 |
| `stdblnull()` | NULL 가능한 double 저장 |

---

## 함수 사용 예제

### 기본 파일 작업 흐름
```c
// 1. 파일 생성
int fd = isbuild("employee", 84, &key, ISINOUT + ISEXCLLOCK);

// 2. 파일 열기
int fd = isopen("employee", ISMANULOCK + ISINOUT);

// 3. 레코드 작성
iswrite(fd, record);

// 4. 레코드 읽기
isread(fd, record, ISFIRST);  // 첫 번째 레코드
isread(fd, record, ISNEXT);   // 다음 레코드

// 5. 파일 닫기
isclose(fd);
```

### 트랜잭션 처리
```c
isbegin();           // 트랜잭션 시작
iswrite(fd, rec1);
iswrite(fd, rec2);
if (error) {
    isrollback();    // 오류 발생 시 롤백
} else {
    iscommit();      // 성공 시 커밋
}
```

---

## 프로젝트 폴더 구조

```
CISAM/
├── demo/                         # 데모 프로젝트
│   ├── src/                      # 소스 코드
│   │   ├── add_indx.c
│   │   ├── add_rcrd.c
│   │   ├── bld_file.c
│   │   ├── chaining.c
│   │   ├── sqntl_rd.c
│   │   ├── transctn.c
│   │   └── upd_file.c
│   └── build/                    # 컴파일된 실행파일
│       ├── add_indx
│       ├── add_rcrd
│       ├── bld_file
│       ├── chaining
│       ├── sqntl_rd
│       ├── transctn
│       └── upd_file
├── include/                      # 헤더 파일
│   ├── isam.h
│   └── decimal.h
├── lib/                          # 라이브러리
│   ├── llib-lisam (C-ISAM 라이브러리)
│   └── 기타 ISAM 관련 라이브러리
├── Makefile                      # 빌드 설정
└── SOURCE_DOCUMENTATION.md       # 이 파일
```

---

## 라이브러리 의존성

- **isam.h**: C-ISAM 헤더 파일 (include/ 디렉토리)
- **-lisam**: C-ISAM 라이브러리 (lib/ 디렉토리의 llib-lisam)

---

## 참고 사항

- 모든 프로그램은 IBM의 C-ISAM 라이브러리를 사용합니다
- 원본 예제 파일: ex1.c ~ ex7.c로부터 파생
- 직원 파일과 성과 파일 간의 관계: 직원 번호를 통한 1:N 관계
- 빌드 타겟: `make help` 명령어로 사용 가능한 모든 옵션 확인 가능
