"""查询结果缓存"""
import json
import time
import hashlib
from typing import Optional, Any, Callable
from functools import wraps


class QueryCache:
    """简单的内存缓存"""

    _instance = None
    _cache: dict = {}
    _ttl: dict = {}  # key -> expiry timestamp

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._cache = {}
            cls._instance._ttl = {}
        return cls._instance

    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        if key in self._cache:
            if key in self._ttl and time.time() > self._ttl[key]:
                del self._cache[key]
                del self._ttl[key]
                return None
            return self._cache[key]
        return None

    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """设置缓存，ttl 单位秒"""
        self._cache[key] = value
        self._ttl[key] = time.time() + ttl

    def invalidate(self, key: str) -> None:
        """失效缓存"""
        self._cache.pop(key, None)
        self._ttl.pop(key, None)

    def invalidate_pattern(self, pattern: str) -> None:
        """按模式失效缓存"""
        keys_to_remove = [k for k in self._cache if pattern in k]
        for key in keys_to_remove:
            self.invalidate(key)

    def clear(self) -> None:
        """清空缓存"""
        self._cache.clear()
        self._ttl.clear()

    def stats(self) -> dict:
        """缓存统计"""
        return {
            "total_keys": len(self._cache),
            "valid_keys": sum(1 for k in self._cache if k not in self._ttl or time.time() <= self._ttl[k]),
        }


def cache_key(project_id: str, graph_type: str, **kwargs) -> str:
    """生成缓存键"""
    params = json.dumps(kwargs, sort_keys=True)
    raw = f"{project_id}:{graph_type}:{params}"
    return hashlib.md5(raw.encode()).hexdigest()


def cached_query(ttl: int = 300):
    """缓存装饰器"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache = QueryCache()
            key = func.__name__ + ":" + hashlib.md5(
                json.dumps(list(args) + sorted(kwargs.items()), sort_keys=True).encode()
            ).hexdigest()

            result = cache.get(key)
            if result is not None:
                return result

            result = await func(*args, **kwargs)
            cache.set(key, result, ttl)
            return result
        return wrapper
    return decorator


# 全局实例
query_cache = QueryCache()
