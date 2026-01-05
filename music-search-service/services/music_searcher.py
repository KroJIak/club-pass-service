"""Music searcher service using MusicAPI and Yandex Music."""
import requests
from yandex_music import Client
from typing import List, Dict, Optional
import difflib
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Track:
    """Класс для представления трека"""
    title: str
    artist: str
    source: str
    links: Dict[str, Optional[str]]
    album: Optional[str] = None
    release_date: Optional[str] = None
    track_id: Optional[str] = None


class MusicSearcher:
    """Универсальный поисковик музыки через MusicAPI и Yandex Music"""
    
    def __init__(self, yandex_token: str, music_api_base: str = "https://bhindi1.ddns.net/music/api"):
        """
        Инициализация поисковика
        
        Args:
            yandex_token (str): OAuth токен Яндекс.Музыки
            music_api_base (str): Базовый URL MusicAPI
        """
        self.yandex_client = Client(yandex_token).init()
        self.music_api_base = music_api_base
        
    def search_music_api(self, query: str) -> List[Track]:
        """
        Поиск в MusicAPI (YouTube + Spotify + Audio)
        
        Args:
            query (str): Поисковый запрос (название или исполнитель - название)
        
        Returns:
            List[Track]: Список найденных треков
        """
        logger.info(f"🔍 MusicAPI: Начинаю поиск для запроса: '{query}'")
        try:
            # Подготовка запроса
            prepare_url = f"{self.music_api_base}/prepare/{query}"
            logger.info(f"📡 MusicAPI: Отправляю запрос на prepare: {prepare_url}")
            response1 = requests.get(
                prepare_url,
                timeout=10
            )
            logger.info(f"📡 MusicAPI: Получен ответ prepare, статус: {response1.status_code}")
            response1.raise_for_status()
            
            data1 = response1.json()
            logger.info(f"📡 MusicAPI: Данные prepare: {data1}")
            if 'song_id' not in data1:
                logger.warning(f"⚠️ MusicAPI: В ответе prepare нет 'song_id', данные: {data1}")
                return []
            
            song_id = data1['song_id']
            logger.info(f"✅ MusicAPI: Получен song_id: {song_id}")
            
            # Получение полных данных
            fetch_url = f"{self.music_api_base}/fetch/{song_id}"
            logger.info(f"📡 MusicAPI: Отправляю запрос на fetch: {fetch_url}")
            response2 = requests.get(
                fetch_url,
                timeout=10
            )
            logger.info(f"📡 MusicAPI: Получен ответ fetch, статус: {response2.status_code}")
            response2.raise_for_status()
            
            data2 = response2.json()
            logger.info(f"📡 MusicAPI: Данные fetch: {data2}")
            
            # Парсинг результата
            track = Track(
                title=data2.get('title', 'Unknown'),
                artist=data2.get('artist', 'Unknown'),
                source='MusicAPI',
                links={
                    'youtube': data2.get('youtube_url'),
                    'spotify': data2.get('spotify_url'),
                    'audio': data2.get('audio_url'),
                    'soundcloud': data2.get('soundcloud_url'),
                    'apple_music': data2.get('apple_music_url')
                },
                album=data2.get('album'),
                track_id=song_id
            )
            
            logger.info(f"✅ MusicAPI: Успешно создан трек: {track.artist} - {track.title}")
            return [track]
        
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ MusicAPI: Ошибка запроса: {e}", exc_info=True)
            return []
        except Exception as e:
            logger.error(f"❌ MusicAPI: Неожиданная ошибка: {e}", exc_info=True)
            return []
    
    def search_yandex_music(self, query: str) -> List[Track]:
        """
        Поиск в Yandex Music
        
        Args:
            query (str): Поисковый запрос
        
        Returns:
            List[Track]: Список найденных треков
        """
        logger.info(f"🔍 Yandex Music: Начинаю поиск для запроса: '{query}'")
        try:
            results = self.yandex_client.search(query)
            logger.info(f"📡 Yandex Music: Получены результаты поиска")
            
            if not results.tracks or not results.tracks.results:
                logger.warning(f"⚠️ Yandex Music: Нет результатов треков для запроса: '{query}'")
                return []
            
            logger.info(f"📡 Yandex Music: Найдено треков: {len(results.tracks.results)}")
            tracks = []
            for i, track in enumerate(results.tracks.results[:5], 1):  # Топ 5 результатов
                yandex_link = f"https://music.yandex.ru/album/{track.albums[0].id}/track/{track.id}" if track.albums else None
                
                track_obj = Track(
                    title=track.title,
                    artist=track.artists[0].name if track.artists else 'Unknown',
                    source='Yandex Music',
                    links={
                        'yandex_music': yandex_link
                    },
                    album=track.albums[0].title if track.albums else None,
                    release_date=track.albums[0].release_date if track.albums else None,
                    track_id=str(track.id) if track.id else None
                )
                logger.info(f"✅ Yandex Music [{i}]: {track_obj.artist} - {track_obj.title}")
                tracks.append(track_obj)
            
            logger.info(f"✅ Yandex Music: Всего обработано треков: {len(tracks)}")
            return tracks
        
        except Exception as e:
            logger.error(f"❌ Yandex Music: Ошибка: {e}", exc_info=True)
            return []
    
    def _match_similarity(self, query: str, title: str, artist: str) -> float:
        """
        Вычисление схожести между запросом и результатом
        
        Args:
            query (str): Исходный запрос
            title (str): Название трека
            artist (str): Исполнитель
        
        Returns:
            float: Коэффициент схожести (0-1)
        """
        full_text = f"{title} {artist}".lower()
        query_lower = query.lower()
        
        # Проверяем наличие подстрок
        similarity = difflib.SequenceMatcher(None, query_lower, full_text).ratio()
        return similarity
    
    def search(self, song_title: str, artist: Optional[str] = None, 
              min_similarity: float = 0.3) -> Dict[str, List[Track]]:
        """
        Единый поиск по обоим источникам с фильтром по подстроке
        
        Args:
            song_title (str): Название песни
            artist (Optional[str]): Исполнитель (опционально)
            min_similarity (float): Минимальный коэффициент схожести (0-1)
        
        Returns:
            Dict[str, List[Track]]: Результаты из разных источников
        """
        # Формируем поисковый запрос
        if artist:
            query = f"{artist} - {song_title}"
        else:
            query = song_title
        
        logger.info(f"🔍 Начинаю поиск: song_title='{song_title}', artist='{artist}', query='{query}', min_similarity={min_similarity}")
        
        results = {
            'music_api': [],
            'yandex_music': []
        }
        
        # Поиск в MusicAPI
        logger.info("=" * 60)
        logger.info("📡 Поиск в MusicAPI...")
        music_api_results = self.search_music_api(query)
        logger.info(f"📡 MusicAPI: Найдено треков до фильтрации: {len(music_api_results)}")
        
        # Фильтр по схожести для MusicAPI
        filtered_music_api = []
        for track in music_api_results:
            similarity = self._match_similarity(query, track.title, track.artist)
            logger.info(f"📊 MusicAPI: '{track.artist} - {track.title}' - схожесть: {similarity:.2f} (порог: {min_similarity})")
            if similarity >= min_similarity:
                filtered_music_api.append(track)
                logger.info(f"✅ MusicAPI: Трек прошел фильтр")
            else:
                logger.info(f"❌ MusicAPI: Трек не прошел фильтр (схожесть {similarity:.2f} < {min_similarity})")
        
        results['music_api'] = filtered_music_api
        logger.info(f"✅ MusicAPI: После фильтрации: {len(filtered_music_api)} треков")
        
        # Поиск в Yandex Music
        logger.info("=" * 60)
        logger.info("📡 Поиск в Yandex Music...")
        yandex_results = self.search_yandex_music(query)
        logger.info(f"📡 Yandex Music: Найдено треков до фильтрации: {len(yandex_results)}")
        
        # Фильтр по схожести для Yandex Music
        filtered_yandex = []
        for track in yandex_results:
            similarity = self._match_similarity(query, track.title, track.artist)
            logger.info(f"📊 Yandex Music: '{track.artist} - {track.title}' - схожесть: {similarity:.2f} (порог: {min_similarity})")
            if similarity >= min_similarity:
                filtered_yandex.append(track)
                logger.info(f"✅ Yandex Music: Трек прошел фильтр")
            else:
                logger.info(f"❌ Yandex Music: Трек не прошел фильтр (схожесть {similarity:.2f} < {min_similarity})")
        
        results['yandex_music'] = filtered_yandex
        logger.info(f"✅ Yandex Music: После фильтрации: {len(filtered_yandex)} треков")
        
        logger.info("=" * 60)
        logger.info(f"📊 ИТОГО: MusicAPI={len(results['music_api'])}, Yandex Music={len(results['yandex_music'])}")
        
        return results
    
    def search_advanced(self, song_title: str, artist: Optional[str] = None,
                       min_similarity: float = 0.3,
                       search_both: bool = True) -> List[Track]:
        """
        Продвинутый поиск с объединением результатов
        
        Args:
            song_title (str): Название песни
            artist (Optional[str]): Исполнитель
            min_similarity (float): Минимальный коэффициент схожести
            search_both (bool): Искать в обоих источниках
        
        Returns:
            List[Track]: Объединенный список уникальных треков
        """
        logger.info(f"🚀 search_advanced: song_title='{song_title}', artist='{artist}', min_similarity={min_similarity}")
        results = self.search(song_title, artist, min_similarity)
        
        # Объединяем результаты
        all_tracks = results['music_api'] + results['yandex_music']
        logger.info(f"📊 Объединение: всего треков до удаления дубликатов: {len(all_tracks)}")
        
        # Удаляем дубликаты по названию и исполнителю
        seen = set()
        unique_tracks = []
        
        for track in all_tracks:
            key = (track.title.lower(), track.artist.lower())
            if key not in seen:
                seen.add(key)
                unique_tracks.append(track)
                logger.info(f"✅ Уникальный трек: {track.artist} - {track.title} (источник: {track.source})")
            else:
                logger.info(f"🔄 Дубликат пропущен: {track.artist} - {track.title} (источник: {track.source})")
        
        logger.info(f"✅ search_advanced: Итого уникальных треков: {len(unique_tracks)}")
        return unique_tracks

