# Monster Study Tracker - 管理ダッシュボード

Monster Study Tracker の講師向け管理ダッシュボード。学習カリキュラム連携のための新規システム。

既存の受講生向けアプリ（`study_app`）とは別リポジトリとして開発し、認証・受講生データベースは既存DBを共有する。

詳細仕様は `Monster_Study_Tracker_要件定義書_v3_3.docx` を参照。

## 構成

```
.
├── backend/    Django REST Framework（既存study_appのbackendをベースに、新規app trainee_management を追加）
└── frontend/   Vue.js 3 + Vite（管理ダッシュボード専用）
```

## 技術スタック

| 領域 | 技術 |
| --- | --- |
| バックエンド | Django 5.2 + Django REST Framework |
| フロントエンド | Vue.js 3 + Vite |
| DB | Supabase（PostgreSQL）※既存DBと共有 |
| 認証 | JWT（既存と同一の認証基盤・SECRET_KEYを使用） |

## セットアップ

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate   # Windowsの場合: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # SECRET_KEY・DATABASE_URLを設定
python manage.py migrate
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env       # VITE_API_BASE_URLを設定
npm run dev
```

## 新規Djangoアプリ: trainee_management

要件定義書 5-3 に基づく以下のテーブルを管理する：

- `trainee_profile` - 受講生のステータス・担当メンバー・開始日・完了予定日
- `curriculum_chapter` - カリキュラムの章マスタ
- `curriculum_item` - 各章の小項目マスタ
- `chapter_progress` - 受講生ごとの章別進捗

既存の `accounts`（ユーザー認証）・`study`（学習記録）アプリは変更せず、そのまま利用する。
