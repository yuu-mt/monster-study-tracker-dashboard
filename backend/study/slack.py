import requests
import os


def send_slack_message(message):
    """Slackにメッセージを送信する"""
    webhook_url = os.environ.get('SLACK_WEBHOOK_URL')
    if not webhook_url:
        return

    try:
        requests.post(webhook_url, json={'text': message}, timeout=5)
    except Exception:
        pass

def check_milestone(user, prev_minutes, new_minutes):
    """月間学習時間マイルストーンをチェックして通知"""
    milestones = [
        (600, '10時間'),
        (1200, '20時間'),
        (1800, '30時間'),
        (3000, '50時間'),
    ]

    for minutes, label in milestones:
        if prev_minutes < minutes <= new_minutes:
            send_slack_message(
                f'🎉 *{user.username}* が今月の学習時間 *{label}突破！* 最高！ 📚'
            )
            break

def check_monster_evolution(user, prev_minutes, new_minutes):
    """モンスター進化をチェックして通知"""
    monster_names = {
        'bird': ['ちび雷鳥', '雷鳥', 'サンダーバード', '伝説のサンダーバード'],
        'dragon': ['ちびドラゴン', 'こドラゴン', 'ドラゴン', '伝説のドラゴン'],
        'dino': ['ちびブラキオ', 'ブラキオサウルス', 'でかブラキオ', '古代ブラキオ'],
    }

    stages = [600, 1800, 3600, 6000]

    for i, threshold in enumerate(stages):
        if prev_minutes < threshold <= new_minutes:
            monster_type = user.monster_type
            names = monster_names.get(monster_type, monster_names['bird'])
            if i < len(names):
                send_slack_message(
                    f'🎉 *{user.username}* のモンスターが *{names[i]}* に進化した！ Good-job！'
                )
            break