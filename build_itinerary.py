#!/usr/bin/env python3
"""Build the confirmed London + Paris itinerary map page."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ITINERARY_OUT = ROOT / "itinerary.json"
HTML_OUT = ROOT / "travel-plan.html"


def maps(query: str) -> dict[str, str]:
    from urllib.parse import quote

    encoded = quote(query)
    return {
        "google": f"https://www.google.com/maps/search/?api=1&query={encoded}",
        "apple": f"https://maps.apple.com/?q={encoded}",
    }


def place(id: str, name: str, name_en: str, lat: float, lng: float, kind: str, area: str, note: str = "") -> dict:
    query = f"{name_en}, {area}"
    return {
        "id": id,
        "name": name,
        "nameEn": name_en,
        "lat": lat,
        "lng": lng,
        "type": kind,
        "area": area,
        "note": note,
        "maps": maps(query),
    }


def item(time: str, title: str, place_id: str | None, desc: str, cost: str, detail: str = "", pay: float | None = None) -> dict:
    data = {
        "time": time,
        "title": title,
        "placeId": place_id,
        "desc": desc,
        "detail": detail,
        "cost": cost,
    }
    if pay is not None:
        data["pay"] = pay
    return data


def day(id: str, date: str, title: str, city: str, summary: str, cost: dict, items: list[dict], backup: str = "") -> dict:
    return {
        "id": id,
        "date": date,
        "title": title,
        "city": city,
        "summary": summary,
        "cost": cost,
        "backup": backup,
        "items": items,
    }


def build_data() -> dict:
    sources = [
        {"label": "Buckingham Palace", "url": "https://www.rct.uk/visit/buckingham-palace"},
        {"label": "Westminster Abbey", "url": "https://www.westminster-abbey.org/visit-us/prices-and-entry-times"},
        {"label": "British Museum", "url": "https://www.britishmuseum.org/visit"},
        {"label": "Louvre", "url": "https://www.louvre.fr/en/visit/hours-admission"},
        {"label": "Eiffel Tower", "url": "https://www.toureiffel.paris/en/rates-opening-times"},
        {"label": "Versailles", "url": "https://en.chateauversailles.fr/plan-your-visit/tickets-and-prices"},
        {"label": "Arc de Triomphe", "url": "https://www.paris-arc-de-triomphe.fr/en/visit/practical-information"},
        {"label": "Musee d'Orsay", "url": "https://www.musee-orsay.fr/en/visit/admission-opening-times-tickets"},
        {"label": "Notre-Dame de Paris", "url": "https://www.notredamedeparis.fr/en/visit/"},
    ]

    places = [
        place("point-a-paddington", "伦敦帕丁顿波特A酒店", "Point A Hotel London Paddington", 51.5181, -0.1723, "hotel", "London Paddington", "建议优先选择有空调的 Paddington 住宿。"),
        place("gatwick", "盖特威克机场", "Gatwick Airport", 51.1537, -0.1821, "transport", "London Gatwick"),
        place("buckingham", "白金汉宫国事厅", "Buckingham Palace State Rooms", 51.5014, -0.1419, "spot", "London SW1A", "7/20 13:00 slot；提前到入口。"),
        place("st-james", "圣詹姆斯公园", "St James's Park", 51.5025, -0.1349, "spot", "London SW1A"),
        place("big-ben", "大本钟与议会大厦", "Big Ben and Houses of Parliament", 51.5007, -0.1246, "spot", "London Westminster"),
        place("westminster-pier", "威斯敏斯特码头", "Westminster Pier", 51.5010, -0.1233, "transport", "London Westminster"),
        place("british-museum", "大英博物馆", "British Museum", 51.5194, -0.1270, "spot", "London Bloomsbury"),
        place("westminster-abbey", "威斯敏斯特教堂", "Westminster Abbey", 51.4993, -0.1273, "spot", "London Westminster"),
        place("national-gallery", "国家美术馆", "National Gallery", 51.5089, -0.1283, "spot", "London Trafalgar Square"),
        place("covent-garden", "科文特花园", "Covent Garden", 51.5117, -0.1233, "spot", "London West End"),
        place("seven-sisters", "七姐妹白崖", "Seven Sisters Cliffs", 50.7601, 0.1465, "spot", "East Sussex"),
        place("birling-gap", "伯灵峡", "Birling Gap", 50.7431, 0.2006, "spot", "East Sussex"),
        place("kings-cross", "国王十字车站", "King's Cross Station", 51.5317, -0.1246, "transport", "London"),
        place("cambridge", "剑桥市中心", "Cambridge city centre", 52.2053, 0.1218, "spot", "Cambridge"),
        place("kings-college", "国王学院礼拜堂", "King's College Chapel Cambridge", 52.2043, 0.1165, "spot", "Cambridge"),
        place("river-cam", "康河撑篙", "River Cam Punting", 52.2071, 0.1167, "spot", "Cambridge"),
        place("hyde-park", "海德公园", "Hyde Park", 51.5073, -0.1657, "spot", "London"),
        place("villa-m", "巴黎M别墅酒店", "Villa M Paris", 48.8414, 2.3159, "hotel", "Paris Montparnasse"),
        place("trocadero", "特罗卡德罗广场", "Trocadero", 48.8629, 2.2870, "spot", "Paris"),
        place("eiffel", "埃菲尔铁塔", "Eiffel Tower", 48.8584, 2.2945, "spot", "Paris"),
        place("louvre", "卢浮宫", "Musee du Louvre", 48.8606, 2.3376, "spot", "Paris"),
        place("galeries", "老佛爷百货", "Galeries Lafayette Paris Haussmann", 48.8738, 2.3321, "shop", "Paris Opera"),
        place("printemps", "巴黎春天", "Printemps Haussmann", 48.8735, 2.3295, "shop", "Paris Opera"),
        place("versailles", "凡尔赛宫", "Chateau de Versailles", 48.8049, 2.1204, "spot", "Versailles"),
        place("invalides", "荣军院", "Les Invalides", 48.8566, 2.3126, "spot", "Paris Left Bank"),
        place("alexandre", "亚历山大三世桥", "Pont Alexandre III", 48.8639, 2.3136, "spot", "Paris"),
        place("champs", "香榭丽舍大街", "Champs-Elysees", 48.8698, 2.3076, "shop", "Paris"),
        place("arc", "凯旋门", "Arc de Triomphe", 48.8738, 2.2950, "spot", "Paris"),
        place("orsay", "奥赛博物馆", "Musee d'Orsay", 48.8600, 2.3266, "spot", "Paris"),
        place("notre-dame", "巴黎圣母院", "Notre-Dame de Paris", 48.8530, 2.3499, "spot", "Paris"),
        place("sainte-chapelle", "圣礼拜堂", "Sainte-Chapelle", 48.8554, 2.3450, "spot", "Paris"),
    ]

    days = [
        day(
            "d1",
            "2026-07-20 周一",
            "抵达伦敦 + 白金汉宫 + 议会区外观 + 游船",
            "London",
            "落地日保守安排：先放行李，13:00 保白金汉宫国事厅，换岗不强追。",
            {"activity": "£51-58", "transport": "£20-30", "food": "£25-45", "total": "£96-133 / ¥922-1,277"},
            [
                item("07:00", "抵达盖特威克机场（Gatwick Airport）", "gatwick", "CA847 上海飞伦敦落地；6人建议商务车接机。", "商务车约£120-180/车，约£20-30/人", "入境、取行李和路况都可能拉长时间，今天不追 11:00 换岗。"),
                item("10:30", "酒店放行李：伦敦帕丁顿波特A酒店（Point A Hotel London Paddington）", "point-a-paddington", "先寄存行李、补水、简单整理。", "免费或按酒店政策", "7月优先空调与睡眠质量。", 1),
                item("13:00", "白金汉宫国事厅（Buckingham Palace State Rooms）", "buckingham", "已按 13:00 slot 规划；建议 12:30-12:40 到入口。", "£33/人", "换岗只作为路过项目，赶上就看。", 1),
                item("15:30", "圣詹姆斯公园（St James's Park）到大本钟（Big Ben）外观", "big-ben", "白金汉宫后慢走到议会区，拍大本钟和议会大厦外观。", "免费"),
                item("18:00", "泰晤士河游船（River Thames Cruise）", "westminster-pier", "从威斯敏斯特或伦敦眼一侧上船，往塔桥方向看夜色。", "约£18-25/人"),
                item("晚餐", "南岸/威斯敏斯特/帕丁顿轻餐", None, "落地日不订太硬的餐厅，优先低糖友好的烤肉、鱼、沙拉或中餐热菜。", "约£25-45/人"),
            ],
            "如航班延误，保留白金汉宫，游船改为议会区外观散步。",
        ),
        day(
            "d2",
            "2026-07-21 周二",
            "大英博物馆 + 威斯敏斯特教堂 + 西区",
            "London",
            "上午博物馆，下午补威斯敏斯特教堂，傍晚走西区轻路线。",
            {"activity": "£27.13", "transport": "£8-20", "food": "£45-80", "total": "£80-127 / ¥769-1,220"},
            [
                item("10:30", "大英博物馆（British Museum）", "british-museum", "免费预约；重点看罗塞塔石碑、埃及、希腊和亚述，不超过 2.5 小时。", "免费", "馆内人多，建议只抓重点。", 1),
                item("13:00", "布卢姆茨伯里/苏豪午餐", None, "午餐不要太重，下午还要进教堂。", "约£20-35/人"),
                item("14:30", "威斯敏斯特教堂（Westminster Abbey）", "westminster-abbey", "内部参观挪到 Day2 下午，避开 Day1 白金汉宫冲突。", "约£27.13/人", "", 1),
                item("16:15", "特拉法加广场（Trafalgar Square）与国家美术馆（National Gallery）", "national-gallery", "国家美术馆常设展免费，可短入内。", "免费"),
                item("17:30", "科文特花园（Covent Garden）/唐人街（Chinatown）晚餐", "covent-garden", "中餐或轻餐，照顾高血糖成员，少甜品。", "约£25-45/人"),
            ],
            "如果威斯敏斯特教堂预约不到，改为只看外观，并把国家美术馆时间加长。",
        ),
        day(
            "d3",
            "2026-07-22 周三",
            "七姐妹白崖一日游",
            "East Sussex",
            "优先小团或6人商务车；天气不好就缩短崖边徒步。",
            {"activity": "£70-110", "transport": "已含或£100-160包车分摊", "food": "£30-50", "total": "£100-160 / ¥960-1,536"},
            [
                item("出发前", "复核天气：Seaford / Cuckmere Haven / Birling Gap", "seven-sisters", "风大、下雨或高温都不硬走崖边。", "免费", "白崖边缘脆弱，保持安全距离。"),
                item("上午", "锡福德角/卡克米尔港湾远景", "seven-sisters", "经典远景比硬走全程更适合轻松节奏。", "一日团约£70-110/人"),
                item("下午", "伯灵峡（Birling Gap）/比奇角（Beachy Head）", "birling-gap", "看天气和体力决定步行长度。", "包车约£600-950/车时，人均约£100-160"),
                item("晚餐", "回伦敦后酒店附近简单晚餐", "point-a-paddington", "第二天剑桥，不再安排远距离晚餐。", "约£30-50/人"),
            ],
            "天气差时改伦敦塔桥外观、Borough Market、圣保罗外观和千禧桥。",
        ),
        day(
            "d4",
            "2026-07-23 周四",
            "剑桥一日游",
            "Cambridge",
            "从国王十字出发，抵达剑桥后打车进市中心，减少走路。",
            {"activity": "£35-53", "transport": "£20-40", "food": "£35-60", "total": "£90-153 / ¥864-1,469"},
            [
                item("上午", "伦敦国王十字车站（King's Cross）到剑桥（Cambridge）", "kings-cross", "从 Paddington 先到 King's Cross，再火车去 Cambridge。", "往返估£20-40/人"),
                item("上午", "国王学院礼拜堂（King's College Chapel）", "kings-college", "剑桥核心点，旺季提前确认票务。", "估£15-18/人"),
                item("午餐", "剑桥市中心轻松午餐", "cambridge", "不排重餐，留体力给下午。", "约£15-25/人"),
                item("下午", "康河撑篙（River Cam Punting）", "river-cam", "适合6人一起体验；现场和线上价格可能不同。", "约£20-35/人"),
                item("傍晚", "学院区散步后回伦敦", "cambridge", "三一学院/圣约翰学院外观即可，不把学院全塞满。", "免费"),
            ],
            "若下雨，减少撑篙，改 Fitzwilliam Museum 或咖啡馆休息。",
        ),
        day(
            "d5",
            "2026-07-24 周五",
            "伦敦半天 + 飞巴黎 + 埃菲尔铁塔亮灯",
            "London / Paris",
            "大交通日：上午只做 Paddington 周边，晚上到巴黎看铁塔夜景，不登塔。",
            {"activity": "€0", "transport": "£20-30 + €8-20", "food": "£15-30 + €25-45", "total": "约¥653-1,117"},
            [
                item("09:00", "海德公园（Hyde Park）/肯辛顿花园/诺丁山三选一", "hyde-park", "只做酒店附近轻量活动，避免赶机场。", "免费"),
                item("12:15", "酒店到盖特威克机场（Gatwick Airport）", "point-a-paddington", "U28405 16:30 伦敦飞巴黎；商务车留足时间。", "约£120-180/车，约£20-30/人"),
                item("晚间", "入住巴黎M别墅酒店（Villa M Paris）", "villa-m", "按蒙帕纳斯/巴斯德一带规划。", "住宿另计"),
                item("22:00/23:00", "特罗卡德罗广场（Trocadero）看埃菲尔铁塔亮灯", "trocadero", "只看外观和整点亮灯，不登塔，避免抵达日过累。", "门票€0，交通/打车约€8-20/人"),
                item("晚餐", "Villa M 或蒙帕纳斯附近晚餐", "villa-m", "第一晚不跨城找餐厅。", "约€25-45/人"),
            ],
            "如航班延误，取消铁塔夜景，只在酒店附近晚餐。",
        ),
        day(
            "d6",
            "2026-07-25 周六",
            "卢浮宫 + 奥斯曼大道购物半天",
            "Paris",
            "上午卢浮宫，下午老佛爷/巴黎春天购物，购物预算另计。",
            {"activity": "€32", "transport": "€8-20", "food": "€65-115", "total": "€105-167 / ¥882-1,403"},
            [
                item("上午", "卢浮宫（Musee du Louvre）", "louvre", "非欧洲经济区访客 €32/人；夏季提前预约上午时段。", "€32/人", "只抓三宝和重点展区，别在馆内耗到体力见底。", 1),
                item("午餐", "卢浮宫/歌剧院附近午餐", None, "购物前吃稳一点。", "约€25-45/人"),
                item("下午", "老佛爷百货（Galeries Lafayette）", "galeries", "购物预算另计；先办会员/折扣，付款选当地货币。", "购物另计", "核对退税单、护照号和收据。", 0.5),
                item("下午", "巴黎春天（Printemps Haussmann）", "printemps", "与老佛爷相邻，同半天完成。", "购物另计", "退税材料按人分开放。", 0.5),
                item("晚餐", "歌剧院/九区附近晚餐", "galeries", "购物日不要再跨到很远区域。", "约€40-70/人"),
            ],
            "如果卢浮宫预约不到上午，购物和卢浮宫前后对调。",
        ),
        day(
            "d7",
            "2026-07-26 周日",
            "凡尔赛宫一日游",
            "Versailles",
            "凡尔赛周一闭馆，所以放周日；从 Montparnasse 方向出发更顺。",
            {"activity": "€35", "transport": "€10-25", "food": "€45-75", "total": "€90-135 / ¥756-1,134"},
            [
                item("上午", "巴黎蒙帕纳斯方向前往凡尔赛", "villa-m", "优先 Paris Montparnasse 到 Versailles Chantiers，再步行/打车。", "交通约€10-25/人"),
                item("上午-下午", "凡尔赛宫（Chateau de Versailles）", "versailles", "Passport 全园票 €35/人；注意防晒、补水和队伍。", "€35/人", "怕晒怕挤时只抓宫殿和近处花园。", 1),
                item("午餐", "凡尔赛园区或镇上简餐", "versailles", "不要把午餐排成正式长餐。", "约€20-35/人"),
                item("傍晚", "回巴黎休息", "villa-m", "晚上只安排酒店附近晚餐。", "晚餐约€25-40/人"),
            ],
            "如果天气极端炎热，凡尔赛缩短为半日，下午回巴黎休息。",
        ),
        day(
            "d8",
            "2026-07-27 周一",
            "左岸 + 香街/凯旋门轻松日",
            "Paris",
            "铁塔已挪到第一晚；这天不登塔，改左岸、塞纳河边和凯旋门。",
            {"activity": "€0-38", "transport": "€8-20", "food": "€50-80", "total": "€58-138 / ¥487-1,159"},
            [
                item("上午", "荣军院外观（Les Invalides）", "invalides", "只看外观和广场，不排重馆。", "免费"),
                item("上午", "亚历山大三世桥（Pont Alexandre III）与塞纳河边", "alexandre", "轻松拍照路线。", "免费"),
                item("下午", "奥赛博物馆（Musee d'Orsay，可选）或圣日耳曼德佩", "orsay", "想看印象派选奥赛；想轻松就咖啡街区。", "可选€16/人"),
                item("傍晚", "香榭丽舍大街（Champs-Elysees）到凯旋门（Arc de Triomphe）", "arc", "凯旋门登顶可选；只看外观免费。", "登顶可选€22/人"),
                item("晚餐", "左岸或香街附近晚餐", "champs", "避开纯网红甜食主餐。", "约€50-80/人"),
            ],
            "如果前一天凡尔赛太累，上午延后出发，只保留香街/凯旋门。",
        ),
        day(
            "d9",
            "2026-07-28 周二",
            "巴黎圣母院 + 西岱岛半天 + 机场",
            "Paris",
            "离开日只排半天市中心，预留机场交通。",
            {"activity": "€0-22", "transport": "€20-45", "food": "€25-45", "total": "€45-112 / ¥378-941"},
            [
                item("上午", "巴黎圣母院（Notre-Dame de Paris）", "notre-dame", "免费，建议官方预约；不要买第三方门票。", "免费", "", 1),
                item("上午", "圣礼拜堂（Sainte-Chapelle，可选）", "sainte-chapelle", "时间够再进；航班较早就只看外观。", "可选约€22/人"),
                item("中午", "西岱岛/塞纳河边简餐", "notre-dame", "离开日不安排长餐。", "约€25-45/人"),
                item("午后", "前往机场", "villa-m", "机场未锁定，按 CDG/ORY 预留；6人商务车约€90-150/车。", "约€20-45/人，包车约€15-25/人"),
            ],
            "如航班提前，只保留圣母院外观和机场。",
        ),
    ]

    return {
        "trip": {
            "title": "伦敦 + 巴黎 2026 夏季中文行程单",
            "subtitle": "London + Paris | 2026.7.20-7.28 | 6人",
            "dateRange": "2026-07-20 至 2026-07-28",
            "travelers": 6,
            "exchange": {"GBP_CNY": 9.6, "EUR_CNY": 8.4},
            "budgetNote": "费用不含机票、住宿、购物、签证、保险、电话卡和不可预见打车加价。",
            "style": "轻松节奏，一天一个主区域；餐厅不反向扭曲路线；高血糖成员每餐保留低甜/高蛋白选项。",
            "hotelChoice": "伦敦建议优先 Point A Hotel London Paddington：7月高温下空调和睡眠质量优先于少坐几站地铁。",
        },
        "places": places,
        "days": days,
        "budgetSummary": {
            "london": [
                {"label": "门票/活动", "value": "£216-288/人"},
                {"label": "市内/机场/一日游交通", "value": "£120-220/人"},
                {"label": "餐饮", "value": "£150-265/人"},
                {"label": "伦敦合计", "value": "£486-773/人，约¥4,666-7,421/人"},
                {"label": "控预算要点", "value": "七姐妹选小团、伦敦市内多用公共交通、餐饮控制在 £35-45/天。"},
            ],
            "paris": [
                {"label": "必选门票", "value": "卢浮宫€32 + 凡尔赛€35 = €67/人"},
                {"label": "可选门票", "value": "奥赛€16 + 凯旋门€22 + 圣礼拜堂€22，最多€60/人"},
                {"label": "餐饮", "value": "€210-360/人"},
                {"label": "交通", "value": "€55-130/人"},
                {"label": "巴黎基础合计", "value": "€332-557/人，约¥2,789-4,679/人"},
                {"label": "含全部可选门票", "value": "€392-617/人，约¥3,293-5,183/人"},
            ],
            "total": [
                {"label": "伦敦基础", "value": "约¥4,666-7,421/人"},
                {"label": "巴黎基础", "value": "约¥2,789-4,679/人"},
                {"label": "伦敦+巴黎基础合计", "value": "约¥7,455-12,100/人"},
                {"label": "含巴黎全部可选门票", "value": "约¥7,959-12,604/人"},
            ],
        },
        "bookingPriority": [
            "白金汉宫国事厅（Buckingham Palace State Rooms）：7/20 13:00",
            "卢浮宫（Musee du Louvre）：7/25 上午",
            "凡尔赛宫（Chateau de Versailles）：7/26",
            "威斯敏斯特教堂（Westminster Abbey）：7/21 下午",
            "大英博物馆（British Museum）免费预约：7/21 10:30",
            "七姐妹白崖（Seven Sisters）小团：7/22",
            "剑桥撑篙（River Cam Punting）：7/23",
        ],
        "restaurantBackups": [
            {"name": "OPSO", "area": "Marylebone", "fit": "只作 Marylebone / Regent's Park 附近备选，不作为行程锚点。", "cost": "估£35-60/人"},
            {"name": "Shawarma Bros", "area": "Waterloo", "fit": "只在 South Bank / Waterloo 附近顺路时用。", "cost": "估£12-25/人"},
            {"name": "Ergon Deli", "area": "待确认具体地址", "fit": "需补地址后判断是否顺路。", "cost": "估£20-35/人"},
        ],
        "sources": sources,
    }


HTML_TEMPLATE = r"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>伦敦 + 巴黎中文行程单</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <style>
    :root {
      --bg: #f6f7f2;
      --ink: #17211b;
      --muted: #667266;
      --line: #dfe5dc;
      --card: #ffffff;
      --green: #1f6f4a;
      --blue: #235d8f;
      --red: #9f3a38;
      --gold: #996d1b;
      --shadow: 0 18px 44px rgba(28, 38, 31, .12);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
      color: var(--ink);
      background: var(--bg);
    }
    a { color: inherit; }
    button, input, select { font: inherit; }
    .app { display: grid; grid-template-columns: 430px minmax(0, 1fr); min-height: 100vh; }
    aside {
      height: 100vh;
      overflow: auto;
      background: rgba(255,255,255,.92);
      border-right: 1px solid var(--line);
      padding: 18px;
    }
    main { min-width: 0; display: grid; grid-template-rows: minmax(360px, 56vh) 1fr; }
    #map { width: 100%; min-height: 360px; z-index: 1; }
    .hero {
      padding: 18px;
      border: 1px solid var(--line);
      background: linear-gradient(135deg, #fdfbf3, #eef6f2);
      box-shadow: var(--shadow);
      border-radius: 8px;
    }
    .eyebrow { margin: 0 0 6px; color: var(--green); font-weight: 800; font-size: 12px; letter-spacing: .08em; text-transform: uppercase; }
    h1 { margin: 0; font-size: 28px; line-height: 1.15; letter-spacing: 0; }
    .meta { margin: 8px 0 0; color: var(--muted); line-height: 1.6; font-size: 13px; }
    .tabs { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin: 14px 0; }
    .tab {
      min-height: 44px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fff;
      color: var(--muted);
      cursor: pointer;
      font-weight: 700;
    }
    .tab.active { background: var(--green); border-color: var(--green); color: #fff; }
    .section { padding: 14px 18px 18px; overflow: auto; }
    .summary-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 16px; }
    .summary-box, .card {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--card);
      box-shadow: 0 8px 22px rgba(28,38,31,.06);
    }
    .summary-box { padding: 14px; }
    .summary-box h3 { margin: 0 0 8px; font-size: 14px; color: var(--green); }
    .summary-box p { margin: 4px 0; color: var(--muted); font-size: 13px; line-height: 1.45; }
    .day-head { margin: 0 0 12px; }
    .day-head h2 { margin: 0; font-size: 22px; letter-spacing: 0; }
    .day-head p { margin: 6px 0 0; color: var(--muted); line-height: 1.5; }
    .cards { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
    .card { padding: 14px; position: relative; min-height: 170px; }
    .card h3 { margin: 0 0 6px; font-size: 16px; letter-spacing: 0; }
    .time { color: var(--blue); font-weight: 800; font-size: 13px; }
    .desc, .detail { color: var(--muted); font-size: 13px; line-height: 1.55; }
    .cost { color: var(--gold); font-size: 13px; font-weight: 800; margin-top: 8px; }
    .chips { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 10px; }
    .chip {
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 6px 9px;
      font-size: 12px;
      text-decoration: none;
      background: #fbfcfa;
      color: var(--muted);
    }
    .pay-yes { border-color: rgba(31,111,74,.25); color: var(--green); background: #edf8f1; }
    .pay-maybe { border-color: rgba(153,109,27,.25); color: var(--gold); background: #fff8e8; }
    .backup {
      margin-top: 12px;
      border-left: 4px solid var(--gold);
      background: #fff9ea;
      padding: 10px 12px;
      border-radius: 6px;
      color: #675327;
      font-size: 13px;
      line-height: 1.5;
    }
    .lists { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
    .list { padding: 14px; }
    .list h3 { margin: 0 0 8px; font-size: 15px; }
    .list ol, .list ul { margin: 0; padding-left: 18px; color: var(--muted); font-size: 13px; line-height: 1.7; }
    .leaflet-popup-content { margin: 10px 12px; min-width: 190px; }
    .popup-title { font-weight: 800; margin-bottom: 4px; }
    .popup-en { color: #667266; font-size: 12px; }
    .popup-type { color: #1f6f4a; font-size: 12px; margin-top: 4px; }
    @media (max-width: 920px) {
      .app { display: block; }
      aside { height: auto; max-height: none; border-right: 0; border-bottom: 1px solid var(--line); }
      main { display: block; }
      #map { height: 420px; }
      .summary-grid, .cards, .lists { grid-template-columns: 1fr; }
      .tabs { grid-template-columns: repeat(3, 1fr); }
    }
    @media (max-width: 480px) {
      aside, .section { padding: 12px; }
      h1 { font-size: 23px; }
      .tabs { grid-template-columns: repeat(2, 1fr); }
      .tab { min-height: 42px; font-size: 13px; }
      #map { height: 360px; }
    }
  </style>
</head>
<body>
  <div class="app">
    <aside>
      <div class="hero">
        <p class="eyebrow">Reference itinerary</p>
        <h1 id="trip-title"></h1>
        <p id="trip-meta" class="meta"></p>
        <p id="trip-note" class="meta"></p>
      </div>
      <div id="tabs" class="tabs" aria-label="每日行程"></div>
      <div class="lists">
        <div class="summary-box">
          <h3>订票优先级</h3>
          <ol id="booking"></ol>
        </div>
        <div class="summary-box">
          <h3>餐厅备选池</h3>
          <ul id="restaurants"></ul>
        </div>
      </div>
    </aside>
    <main>
      <div id="map"></div>
      <section class="section">
        <div class="summary-grid" id="budget-summary"></div>
        <div class="day-head">
          <h2 id="day-title"></h2>
          <p id="day-summary"></p>
        </div>
        <div id="cards" class="cards"></div>
        <div id="backup" class="backup"></div>
        <div class="lists" style="margin-top:12px">
          <div class="summary-box">
            <h3>支付与预算提醒</h3>
            <p>Apple Pay / Visa 优先；支付宝和微信境外 NFC 不作为唯一支付方式。购物付款选当地货币，退税单据按人分开。</p>
          </div>
          <div class="summary-box">
            <h3>来源</h3>
            <ul id="sources"></ul>
          </div>
        </div>
      </section>
    </main>
  </div>
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <script id="trip-data" type="application/json">__DATA__</script>
  <script>
    const data = JSON.parse(document.getElementById('trip-data').textContent);
    const places = new Map(data.places.map(place => [place.id, place]));
    let active = data.days[0].id;
    let map;
    let markers = [];
    const $ = id => document.getElementById(id);
    const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;', "'":'&#39;'}[char]));

    function day() { return data.days.find(d => d.id === active) || data.days[0]; }
    function cityCenter(dayData) {
      if (dayData.city === 'Paris') return [48.8589, 2.3350, 12];
      if (dayData.city === 'Versailles') return [48.8049, 2.1204, 13];
      if (dayData.city === 'Cambridge') return [52.2053, 0.1218, 13];
      if (dayData.city === 'East Sussex') return [50.7520, 0.1800, 11];
      if (dayData.city.includes('Paris')) return [50.6, 0.9, 6];
      return [51.5074, -0.1278, 12];
    }
    function init() {
      $('trip-title').textContent = data.trip.title;
      $('trip-meta').textContent = `${data.trip.subtitle} · ${data.trip.dateRange}`;
      $('trip-note').textContent = `${data.trip.style} ${data.trip.budgetNote}`;
      $('booking').innerHTML = data.bookingPriority.map(item => `<li>${esc(item)}</li>`).join('');
      $('restaurants').innerHTML = data.restaurantBackups.map(item => `<li><strong>${esc(item.name)}</strong>：${esc(item.fit)} ${esc(item.cost)}</li>`).join('');
      $('sources').innerHTML = data.sources.map(source => `<li><a href="${esc(source.url)}" target="_blank" rel="noreferrer">${esc(source.label)}</a></li>`).join('');
      renderTabs();
      map = L.map('map', { scrollWheelZoom: false });
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; OpenStreetMap contributors'
      }).addTo(map);
      render();
    }
    function renderTabs() {
      $('tabs').innerHTML = data.days.map((d, idx) => `<button type="button" class="tab ${d.id === active ? 'active' : ''}" data-id="${esc(d.id)}">D${idx + 1}<br>${esc(d.date.slice(5))}</button>`).join('');
      document.querySelectorAll('.tab').forEach(button => button.addEventListener('click', () => {
        active = button.dataset.id;
        renderTabs();
        render();
      }));
    }
    function budgetBox(title, rows) {
      return `<div class="summary-box"><h3>${esc(title)}</h3>${rows.map(row => `<p><strong>${esc(row.label)}：</strong>${esc(row.value)}</p>`).join('')}</div>`;
    }
    function payChip(item) {
      if (item.pay === 1) return '<span class="chip pay-yes">建议提前预订/确认</span>';
      if (item.pay === 0.5) return '<span class="chip pay-maybe">购物/退税注意</span>';
      return '';
    }
    function card(item) {
      const place = item.placeId ? places.get(item.placeId) : null;
      const mapLinks = place?.maps || {};
      return `<article class="card">
        <div class="time">${esc(item.time)}</div>
        <h3>${esc(item.title)}</h3>
        <p class="desc">${esc(item.desc)}</p>
        ${item.detail ? `<p class="detail">${esc(item.detail)}</p>` : ''}
        <p class="cost">${esc(item.cost)}</p>
        <div class="chips">
          ${payChip(item)}
          ${mapLinks.google ? `<a class="chip" href="${esc(mapLinks.google)}" target="_blank" rel="noreferrer">Google Maps</a>` : ''}
          ${mapLinks.apple ? `<a class="chip" href="${esc(mapLinks.apple)}" target="_blank" rel="noreferrer">Apple Maps</a>` : ''}
        </div>
      </article>`;
    }
    function renderMarkers(dayData) {
      markers.forEach(marker => marker.remove());
      markers = [];
      const bounds = [];
      dayData.items.forEach((item, index) => {
        const place = item.placeId ? places.get(item.placeId) : null;
        if (!place || typeof place.lat !== 'number') return;
        const marker = L.marker([place.lat, place.lng]).addTo(map);
        marker.bindPopup(`<div class="popup-title">${index + 1}. ${esc(place.name)}</div><div class="popup-en">${esc(place.nameEn)}</div><div class="popup-type">${esc(item.time)} · ${esc(item.cost)}</div>`);
        markers.push(marker);
        bounds.push([place.lat, place.lng]);
      });
      if (bounds.length > 1) map.fitBounds(bounds, { padding: [28, 28] });
      else {
        const [lat, lng, zoom] = cityCenter(dayData);
        map.setView([lat, lng], zoom);
      }
    }
    function render() {
      const d = day();
      $('budget-summary').innerHTML = [
        budgetBox('伦敦预计费用', data.budgetSummary.london),
        budgetBox('巴黎预计费用', data.budgetSummary.paris),
        budgetBox('全程预计费用', data.budgetSummary.total),
      ].join('');
      $('day-title').textContent = `${d.date} · ${d.title}`;
      $('day-summary').textContent = `${d.summary} 当日估算：${d.cost.total}`;
      $('cards').innerHTML = d.items.map(card).join('');
      $('backup').textContent = `天气/延误备选：${d.backup}`;
      renderMarkers(d);
    }
    init();
  </script>
</body>
</html>
"""


def main() -> int:
    data = build_data()
    ITINERARY_OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    html = HTML_TEMPLATE.replace("__DATA__", json.dumps(data, ensure_ascii=False))
    HTML_OUT.write_text(html, encoding="utf-8")
    print(f"Wrote {ITINERARY_OUT.name} and {HTML_OUT.name} for {len(data['days'])} days")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
