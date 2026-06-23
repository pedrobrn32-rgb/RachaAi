"""
Cache local em memória para Streamlit - evita reruns desnecessários
"""
import streamlit as st
from datetime import datetime, timedelta
from typing import Any

class StreamlitCache:
    """Cache thread-safe integrado com session_state do Streamlit"""
    
    @staticmethod
    def init():
        """Inicializa estrutura de cache no session_state"""
        if "cache" not in st.session_state:
            st.session_state.cache = {
                "data": {},
                "timestamps": {},
            }
    
    @staticmethod
    def get(key: str, ttl_secs: int = 300) -> Any | None:
        """Retorna valor do cache se ainda válido"""
        StreamlitCache.init()
        cache = st.session_state.cache
        
        if key not in cache["data"]:
            return None
        
        age = (datetime.now() - cache["timestamps"][key]).total_seconds()
        if age > ttl_secs:
            del cache["data"][key]
            del cache["timestamps"][key]
            return None
        
        return cache["data"][key]
    
    @staticmethod
    def set(key: str, value: Any):
        """Armazena valor no cache"""
        StreamlitCache.init()
        cache = st.session_state.cache
        cache["data"][key] = value
        cache["timestamps"][key] = datetime.now()
    
    @staticmethod
    def delete(key: str):
        """Remove valor específico"""
        StreamlitCache.init()
        cache = st.session_state.cache
        cache["data"].pop(key, None)
        cache["timestamps"].pop(key, None)
    
    @staticmethod
    def clear():
        """Limpa todo o cache"""
        if "cache" in st.session_state:
            st.session_state.cache = {"data": {}, "timestamps": {}}
