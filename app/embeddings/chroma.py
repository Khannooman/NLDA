import logging
from typing import List, Dict
import os
from app.enums.env_keys import EnvKeys
from app.utils.utility_manager import UtilityManager

from langchain_core.documents import Document
from langchain_chroma.vectorstores import Chroma
from langchain_openai.embeddings import OpenAIEmbeddings

class VectorSearch(UtilityManager):
    def __init__(self):
        super().__init__()
        self.__OPENAI_API_KEY = self.get_env_variable(EnvKeys.OPENAI_KEY.value)
        self.__EMBEDDING_MODEL = self.get_env_variable(EnvKeys.OPENAI_EMBEDDING_MODEL.value)

        os.environ['OPENAI_API_KEY'] = self.__OPENAI_API_KEY
        self.__EMBEDDINGS = OpenAIEmbeddings(
            model=self.__EMBEDDING_MODEL,
        )
        self.persist_dorictory = self.get_env_variable(EnvKeys.CHROMA_PERSIST_DIRECTORY.value)

    def get_vector(self, collection_name: str) -> Chroma:
        """create vectorstore

        Args:
            persist_directory (str): directory to store embedding
            collection_name (str, optional): vectore collection names. Defaults to "vectorstore".
        Returns:
            Chroma: return chroma instance
        """
        vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=self.__EMBEDDINGS,
            persist_directory=self.persist_dorictory
        )
        return vectorstore
    
    def create_vector_embeddings(
            self,
            docs: List[Document],
            session_id: str
            ) -> Dict:
        """create vecotor embedding

        Args:
            docs (List[Document]): List of Text Documents
            session_id (str): current_session_id,
            persist_directory (str): location of chroma directory
        Returns:
            Dict: return embedding
        """
        try:
            collection_name = f"schema_{session_id}"
            result = self.get_vector(
                        collection_name=collection_name
                        ).from_documents(
                                documents=docs,
                                embedding=self.__EMBEDDINGS,
                                collection_name=collection_name,
                                persist_directory=self.persist_dorictory
                            )
            
            logging.info(f"Stored schema embedding for session {session_id}")
        except Exception as e:
            logging.error(f"Failed to store schema embedding {str(e)}")
            raise

    def search_in_vector(
            self, 
            query: str,
            top_k: int,
            session_id: str
            ) -> Dict:
        try:
            # If collection found then search
            collection_name = f"schema_{session_id}"
            vector_store = self.get_vector(collection_name)
            results = vector_store.similarity_search(query=query, k=top_k)
            return results
        
        except Exception as e:
            logging.error(f"Vector search error {str(e)}")
            raise ValueError(f"Fetching tables error {str(e)}")
        
    def delete_vector(
            self, 
            collection_name: str,
            ) -> Dict:
        try:
            vector_store = self.get_vector(collection_name=collection_name)
            vector_store.delete_collection()
            return {"message": "Vector embedding deleting successfully"}
        
        except Exception as e:
            logging.error(f"Deleting embedding error{str(e)}")
            return {"error": f"Deleting embedding error{str(e)}"}



        
    


 