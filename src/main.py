"""Local CLI for request-aware recommendations; no browser login UI yet."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from recommender_function import recommend

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--request',type=Path,required=True,help='Structured request JSON')
    parser.add_argument('--profile',type=Path,help='Private normalized MAL profile JSON; never logged')
    args=parser.parse_args()
    request=json.loads(args.request.read_text(encoding='utf-8'))
    profile=json.loads(args.profile.read_text(encoding='utf-8')) if args.profile else None
    print(json.dumps(recommend(request,profile),ensure_ascii=True,indent=2))

if __name__=='__main__':main()
