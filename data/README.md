# 数据
## [老番茄 一千万粉丝记录](老番茄_一千万粉丝记录.txt)
**老番茄** 一千万粉丝前后粉丝数量（频率为 1 s），其中在达到一千万粉丝时程序正常中止，后来感觉记录前后数据也十分有必要，所以继续记录一段时间。


## [哔哩哔哩漫画 一千万粉丝记录](哔哩哔哩漫画_一千万粉丝记录.txt)
**哔哩哔哩漫画** 一千万粉丝前后粉丝数量（频率为 1 s），吸取教训后一直运行到次日起床。


## [2020-04-05 禁播后热度情况](2020-04-05_禁播后热度情况.txt)
2020 年 4 月 4 日禁娱，次日开播从原先基准热度 813 一直飙升，最后由于凌晨热度下降，通过此数据可以拟合热度下降函数（指数函数）。


## [用户 25956866 收藏夹来源](用户_25956866_收藏夹来源.json)
初步判定用户 25956866 为营销号，此数据为记录其收藏夹收藏视频的用户资料 id，用以查找相似营销号。


## [入驻明星视频数据](入驻明星视频数据.json)
```python
import json
import time
import tqdm

from bilibili.space import User


u = User(354576498)
output_path = '入驻明星视频数据.json'
result = dict()

for favlist in u.favorites:
    if favlist.title == '用作数据分析的明星入驻':
        break
for video in tqdm.tqdm(favlist.videos, total=favlist.number_of_media):
    video.set_info()
    owner = User(video.info['owner'])
    result[owner.id] = dict(
        info=owner.info,
        videos=tuple(v.info for v in owner.videos)
    )
    time.sleep(1)
with open(output_path, 'w') as f:
    json.dump(result, f, ensure_ascii=False)
```
