import sys
import importlib.util

# 3_rag_system.py를 import
spec = importlib.util.spec_from_file_location("rag_system", "3_rag_system.py")
rag_system = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rag_system)
ask = rag_system.ask

if __name__ == "__main__":
    # 테스트 1
    print(ask("iM스마트예금 우대요건 알려줘"))
    print("\n" + "="*50 + "\n")

    # 테스트 2
    print(ask("iM스마트예금 설명해줘"))
    print("\n" + "="*50 + "\n")

    # 테스트 3
    print(ask("개인종합자산관리계좌의 중도해지이자율 알려줘"))
    print("\n" + "="*50 + "\n")

    # 테스트 4
    print(ask("iM스마트예금이랑 iM행복파트너예금 기본이자율 차이를 정리해줘"))
