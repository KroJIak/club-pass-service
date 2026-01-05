"""Music searcher service using Yandex Music."""
from yandex_music import Client
from typing import List, Optional
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
    links: dict[str, Optional[str]]
    album: Optional[str] = None
    release_date: Optional[str] = None
    track_id: Optional[str] = None


class MusicSearcher:
    """Поисковик музыки через Yandex Music"""
    
    def __init__(self, yandex_token: str):
        """
        Инициализация поисковика
        
        Args:
            yandex_token (str): OAuth токен Яндекс.Музыки
        """
        self.yandex_client = Client(yandex_token).init()
    
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
    
    def search_advanced(self, song_title: str, artist: Optional[str] = None,
                       min_similarity: float = 0.3) -> List[Track]:
        """
        Поиск треков через Yandex Music с фильтрацией по схожести
        
        Args:
            song_title (str): Название песни
            artist (Optional[str]): Исполнитель
            min_similarity (float): Минимальный коэффициент схожести
        
        Returns:
            List[Track]: Список найденных треков
        """
        # Формируем поисковый запрос
        if artist:
            query = f"{artist} - {song_title}"
        else:
            query = song_title
        
        logger.info(f"🚀 search_advanced: song_title='{song_title}', artist='{artist}', query='{query}', min_similarity={min_similarity}")
        
        # Поиск в Yandex Music
        logger.info("=" * 60)
        logger.info("📡 Поиск в Yandex Music...")
        yandex_results = self.search_yandex_music(query)
        logger.info(f"📡 Yandex Music: Найдено треков до фильтрации: {len(yandex_results)}")
        
        # Фильтр по схожести
        filtered_tracks = []
        for track in yandex_results:
            similarity = self._match_similarity(query, track.title, track.artist)
            logger.info(f"📊 Yandex Music: '{track.artist} - {track.title}' - схожесть: {similarity:.2f} (порог: {min_similarity})")
            if similarity >= min_similarity:
                filtered_tracks.append(track)
                logger.info(f"✅ Yandex Music: Трек прошел фильтр")
            else:
                logger.info(f"❌ Yandex Music: Трек не прошел фильтр (схожесть {similarity:.2f} < {min_similarity})")
        
        logger.info("=" * 60)
        logger.info(f"✅ search_advanced: Итого треков: {len(filtered_tracks)}")
        return filtered_tracks
