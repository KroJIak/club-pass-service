"""Music searcher service using MusicAPI and Yandex Music."""
import requests
from yandex_music import Client
from typing import List, Dict, Optional
import difflib
from dataclasses import dataclass


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
        try:
            # Подготовка запроса
            response1 = requests.get(
                f"{self.music_api_base}/prepare/{query}",
                timeout=10
            )
            response1.raise_for_status()
            
            data1 = response1.json()
            if 'song_id' not in data1:
                return []
            
            song_id = data1['song_id']
            
            # Получение полных данных
            response2 = requests.get(
                f"{self.music_api_base}/fetch/{song_id}",
                timeout=10
            )
            response2.raise_for_status()
            
            data2 = response2.json()
            
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
            
            return [track]
        
        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка MusicAPI: {e}")
            return []
        except Exception as e:
            print(f"❌ Неожиданная ошибка при поиске в MusicAPI: {e}")
            return []
    
    def search_yandex_music(self, query: str) -> List[Track]:
        """
        Поиск в Yandex Music
        
        Args:
            query (str): Поисковый запрос
        
        Returns:
            List[Track]: Список найденных треков
        """
        try:
            results = self.yandex_client.search(query)
            
            if not results.tracks or not results.tracks.results:
                return []
            
            tracks = []
            for track in results.tracks.results[:5]:  # Топ 5 результатов
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
                tracks.append(track_obj)
            
            return tracks
        
        except Exception as e:
            print(f"❌ Ошибка Yandex Music: {e}")
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
        
        results = {
            'music_api': [],
            'yandex_music': []
        }
        
        # Поиск в MusicAPI
        music_api_results = self.search_music_api(query)
        
        # Фильтр по схожести для MusicAPI
        filtered_music_api = [
            track for track in music_api_results
            if self._match_similarity(query, track.title, track.artist) >= min_similarity
        ]
        results['music_api'] = filtered_music_api
        
        # Поиск в Yandex Music
        yandex_results = self.search_yandex_music(query)
        
        # Фильтр по схожести для Yandex Music
        filtered_yandex = [
            track for track in yandex_results
            if self._match_similarity(query, track.title, track.artist) >= min_similarity
        ]
        results['yandex_music'] = filtered_yandex
        
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
        results = self.search(song_title, artist, min_similarity)
        
        # Объединяем результаты
        all_tracks = results['music_api'] + results['yandex_music']
        
        # Удаляем дубликаты по названию и исполнителю
        seen = set()
        unique_tracks = []
        
        for track in all_tracks:
            key = (track.title.lower(), track.artist.lower())
            if key not in seen:
                seen.add(key)
                unique_tracks.append(track)
        
        return unique_tracks

