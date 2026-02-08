import os
import re
from pathlib import Path
from typing import List, Dict, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import pickle


class OperationsHandbookRAG:
    def __init__(self, handbook_path: str, model_name: str = "all-MiniLM-L6-v2"):
        self.handbook_path = handbook_path
        self.model = SentenceTransformer(model_name)
        self.chunks: List[Dict[str, str]] = []
        self.embeddings: np.ndarray = None
        self.index: faiss.Index = None
        self.cache_dir = Path("rag/cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def load_and_chunk_handbook(self) -> List[Dict[str, str]]:
        with open(self.handbook_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        sections = re.split(r'\n## ', content)
        chunks = []
        
        for section in sections:
            if not section.strip():
                continue
                
            lines = section.split('\n')
            section_title = lines[0].replace('# ', '').strip()
            
            subsections = re.split(r'\n### ', '\n'.join(lines[1:]))
            
            for subsection in subsections:
                if not subsection.strip():
                    continue
                    
                sub_lines = subsection.split('\n')
                subsection_title = sub_lines[0].strip()
                subsection_content = '\n'.join(sub_lines[1:]).strip()
                
                if len(subsection_content) > 100:
                    chunks.append({
                        'section': section_title,
                        'subsection': subsection_title,
                        'content': subsection_content,
                        'full_text': f"{section_title} - {subsection_title}\n\n{subsection_content}"
                    })
                    
                paragraphs = re.split(r'\n\n+', subsection_content)
                for para in paragraphs:
                    if len(para.strip()) > 50:
                        chunks.append({
                            'section': section_title,
                            'subsection': subsection_title,
                            'content': para.strip(),
                            'full_text': f"{section_title} - {subsection_title}\n\n{para.strip()}"
                        })
        
        self.chunks = chunks
        return chunks
    
    def build_index(self, force_rebuild: bool = False):
        cache_file = self.cache_dir / "handbook_index.pkl"
        
        if not force_rebuild and cache_file.exists():
            print("Loading cached index...")
            with open(cache_file, 'rb') as f:
                cache_data = pickle.load(f)
                self.chunks = cache_data['chunks']
                self.embeddings = cache_data['embeddings']
                self.index = cache_data['index']
            print(f"Loaded {len(self.chunks)} chunks from cache")
            return
        
        print("Building new index...")
        if not self.chunks:
            self.load_and_chunk_handbook()
        
        texts = [chunk['full_text'] for chunk in self.chunks]
        print(f"Encoding {len(texts)} text chunks...")
        self.embeddings = self.model.encode(texts, show_progress_bar=True)
        
        dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(self.embeddings.astype('float32'))
        
        with open(cache_file, 'wb') as f:
            pickle.dump({
                'chunks': self.chunks,
                'embeddings': self.embeddings,
                'index': self.index
            }, f)
        
        print(f"Index built with {len(self.chunks)} chunks")
    
    def search(self, query: str, top_k: int = 5) -> List[Tuple[Dict[str, str], float]]:
        if self.index is None:
            raise ValueError("Index not built. Call build_index() first.")
        
        query_embedding = self.model.encode([query])
        distances, indices = self.index.search(query_embedding.astype('float32'), top_k)
        
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.chunks):
                results.append((self.chunks[idx], float(distance)))
        
        return results
    
    def answer_question(self, question: str, top_k: int = 3) -> Dict[str, any]:
        results = self.search(question, top_k)
        
        context_parts = []
        sources = []
        
        for chunk, score in results:
            context_parts.append(chunk['full_text'])
            sources.append({
                'section': chunk['section'],
                'subsection': chunk['subsection'],
                'relevance_score': 1.0 / (1.0 + score)
            })
        
        context = "\n\n---\n\n".join(context_parts)
        
        answer = self._generate_answer(question, context)
        
        return {
            'question': question,
            'answer': answer,
            'sources': sources,
            'context': context
        }
    
    def _generate_answer(self, question: str, context: str) -> str:
        question_lower = question.lower()
        
        if 'emergency' in question_lower or 'shutdown' in question_lower:
            if 'gpu' in question_lower or 'power' in question_lower:
                return self._extract_procedure(context, 'Emergency Shutdown')
            elif 'cryo' in question_lower or 'valve' in question_lower:
                return self._extract_procedure(context, 'Emergency Shutdown')
        
        if 'startup' in question_lower or 'power up' in question_lower or 'start' in question_lower:
            return self._extract_procedure(context, 'Power-Up Sequence')
        
        if 'shutdown' in question_lower and 'normal' in question_lower:
            return self._extract_procedure(context, 'Normal Shutdown')
        
        if 'troubleshoot' in question_lower or 'problem' in question_lower or 'issue' in question_lower:
            return self._extract_troubleshooting(context)
        
        if 'valve' in question_lower and ('open' in question_lower or 'operate' in question_lower):
            return self._extract_procedure(context, 'Valve Operation')
        
        if 'maintenance' in question_lower or 'schedule' in question_lower:
            return self._extract_maintenance(context)
        
        return self._extract_relevant_info(context, question)
    
    def _extract_procedure(self, context: str, procedure_name: str) -> str:
        lines = context.split('\n')
        in_procedure = False
        procedure_lines = []
        
        for line in lines:
            if procedure_name.lower() in line.lower():
                in_procedure = True
            
            if in_procedure:
                procedure_lines.append(line)
                
                if line.startswith('##') and len(procedure_lines) > 5:
                    break
        
        if procedure_lines:
            return '\n'.join(procedure_lines).strip()
        
        return context[:1000] + "..." if len(context) > 1000 else context
    
    def _extract_troubleshooting(self, context: str) -> str:
        lines = context.split('\n')
        result = []
        
        for i, line in enumerate(lines):
            if 'Problem:' in line or 'Symptoms:' in line or 'Possible Causes:' in line or 'Resolution:' in line:
                result.append(line)
                if i + 1 < len(lines):
                    j = i + 1
                    while j < len(lines) and not lines[j].startswith('####'):
                        result.append(lines[j])
                        j += 1
                        if j - i > 20:
                            break
        
        if result:
            return '\n'.join(result).strip()
        
        return context[:1000] + "..." if len(context) > 1000 else context
    
    def _extract_maintenance(self, context: str) -> str:
        lines = context.split('\n')
        result = []
        in_maintenance = False
        
        for line in lines:
            if 'Maintenance' in line or 'Daily:' in line or 'Weekly:' in line or 'Monthly:' in line or 'Annually:' in line:
                in_maintenance = True
            
            if in_maintenance:
                result.append(line)
                if len(result) > 30:
                    break
        
        if result:
            return '\n'.join(result).strip()
        
        return context[:1000] + "..." if len(context) > 1000 else context
    
    def _extract_relevant_info(self, context: str, question: str) -> str:
        keywords = [word.lower() for word in question.split() if len(word) > 3]
        
        lines = context.split('\n')
        scored_lines = []
        
        for i, line in enumerate(lines):
            score = sum(1 for keyword in keywords if keyword in line.lower())
            if score > 0:
                scored_lines.append((score, i, line))
        
        scored_lines.sort(reverse=True)
        
        if scored_lines:
            relevant_indices = sorted([idx for _, idx, _ in scored_lines[:10]])
            result = []
            for idx in relevant_indices:
                result.append(lines[idx])
            return '\n'.join(result).strip()
        
        return context[:1000] + "..." if len(context) > 1000 else context


def main():
    handbook_path = "docs/OPERATIONS_HANDBOOK.md"
    
    if not os.path.exists(handbook_path):
        print(f"Error: Handbook not found at {handbook_path}")
        return
    
    print("Initializing RAG Assistant...")
    rag = OperationsHandbookRAG(handbook_path)
    
    print("Building index...")
    rag.build_index()
    
    print("\n" + "="*80)
    print("GSE Operations Handbook RAG Assistant")
    print("="*80)
    print("\nExample questions:")
    print("- How do I perform an emergency shutdown of the GPU?")
    print("- What is the startup procedure for the cryogenic line?")
    print("- How do I troubleshoot low voltage on the GPU?")
    print("- What are the maintenance requirements for the cryo valve?")
    print("\nType 'quit' to exit\n")
    
    while True:
        question = input("\nYour question: ").strip()
        
        if question.lower() in ['quit', 'exit', 'q']:
            break
        
        if not question:
            continue
        
        print("\nSearching handbook...")
        result = rag.answer_question(question)
        
        print("\n" + "-"*80)
        print("ANSWER:")
        print("-"*80)
        print(result['answer'])
        
        print("\n" + "-"*80)
        print("SOURCES:")
        print("-"*80)
        for source in result['sources']:
            print(f"- {source['section']} > {source['subsection']} (relevance: {source['relevance_score']:.2f})")


if __name__ == "__main__":
    main()
