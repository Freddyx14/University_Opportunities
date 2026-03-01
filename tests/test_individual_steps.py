"""
SCRIPTS DE TESTING - Ejecutables paso a paso
Para probar cada parte del flujo sin tener que ir por la UI

Cómo usar:
1. Desde la terminal en el root del proyecto
2. Asegúrate que .venv esté activado
3. python tests/test_individual_steps.py
"""

import os
import sys
import json
import tempfile
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment
from dotenv import load_dotenv
load_dotenv()

def separator(title):
    """Print a nice separator"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def test_1_gemini_connection():
    """TEST 1: ¿Gemini está configurado correctamente?"""
    separator("TEST 1: Gemini Connection")
    
    try:
        import google.generativeai as genai
        api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            print("❌ GEMINI_API_KEY no encontrado en .env")
            return False
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-flash-lite-latest")
        
        # Quick test
        response = model.generate_content("Responde solo con: OK")
        
        if "OK" in response.text:
            print("✅ Gemini conectado y funcionando")
            print(f"   API Key: {api_key[:10]}...{api_key[-10:]}")
            return True
        else:
            print(f"⚠️ Respuesta inesperada: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_2_supabase_connection():
    """TEST 2: ¿Supabase está configurado correctamente?"""
    separator("TEST 2: Supabase Connection")
    
    try:
        from src.services.db import _get_supabase_client
        
        supabase = _get_supabase_client()
        
        # Intenta hacer una query simple
        response = supabase.table("students").select("COUNT"). execute()
        
        print("✅ Supabase conectado")
        print(f"   Connection: {supabase.url[:30]}...")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_3_cv_extraction():
    """TEST 3: ¿Se extrae bien el texto del CV?"""
    separator("TEST 3: CV Text Extraction")
    
    try:
        from src.services.ai_agent import GeminiAgent
        
        print("📁 Buscando archivo PDF para testing...")
        
        # Buscar un PDF de test
        test_pdf = Path("tests/sample_cv.pdf")
        if not test_pdf.exists():
            print(f"❓ No se encontró {test_pdf}")
            print("   Creando un CV de test mínimo...")
            
            # Si no existe, crear uno simple para demo
            try:
                from reportlab.pdfgen import canvas
                c = canvas.Canvas(str(test_pdf))
                c.drawString(100, 750, "CV SAMPLE")
                c.drawString(100, 730, "Name: John Doe")
                c.drawString(100, 710, "Degree: Computer Science")
                c.drawString(100, 690, "Skills: Python, React, SQL")
                c.save()
                print(f"   ✓ PDF creado: {test_pdf}")
            except:
                print("   ⚠️ Instala reportlab: pip install reportlab")
                return None
        
        agent = GeminiAgent()
        cv_text = agent.extract_cv_text(str(test_pdf))
        
        if cv_text and len(cv_text) > 50:
            print("✅ CV extraído correctamente")
            print(f"   Longitud: {len(cv_text)} caracteres")
            print(f"   Primeros 200 chars:\n   {cv_text[:200]}...")
            return cv_text
        else:
            print(f"❌ CV muy corto o vacío: {len(cv_text)} chars")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_4_profile_analysis():
    """TEST 4: ¿Se analiza bien el perfil?"""
    separator("TEST 4: Profile Analysis")
    
    try:
        from src.services.ai_agent import GeminiAgent
        
        # Usar CV sample del test anterior
        test_pdf = Path("tests/sample_cv.pdf")
        if not test_pdf.exists():
            print("❌ Primero ejecuta TEST 3 para crear el sample CV")
            return None
        
        agent = GeminiAgent()
        
        print("🔄 Analizando perfil...")
        profile_dict, cv_raw_text = agent.analyze_profile(
            cv_file_path=str(test_pdf),
            audio_file_path=None,
            brain_dump_text="Interesado en becas de IA en Europa"
        )
        
        print("✅ Perfil analizado")
        print(f"\n📋 Datos extraídos:")
        print(f"   Name: {profile_dict.get('name', 'N/A')}")
        print(f"   University: {profile_dict.get('university', 'N/A')}")
        print(f"   Career: {profile_dict.get('career', 'N/A')}")
        print(f"   Country: {profile_dict.get('country', 'N/A')}")
        print(f"   Languages: {profile_dict.get('languages', [])}")
        print(f"   Top Skills: {profile_dict.get('top_skills', [])}")
        print(f"   Interests: {profile_dict.get('interests', [])}")
        print(f"\n📄 CV Raw Text: {len(cv_raw_text)} caracteres")
        print(f"   Primeros 150 chars: {cv_raw_text[:150]}...")
        
        return profile_dict, cv_raw_text
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_5_opportunity_search():
    """TEST 5: ¿Genera bien las oportunidades?"""
    separator("TEST 5: Opportunity Search")
    
    try:
        from src.services.hunter import search_opportunities_with_gemini
        
        # Datos de prueba
        cv_raw_text = """
        Name: John Doe
        Degree: Engineering - Computer Science
        University: PUCP (Pontificia Universidad Católica del Perú)
        Country: Peru
        GPA: 3.8/4.0
        
        Skills:
        - Python (Advanced)
        - JavaScript/React (Intermediate)
        - SQL (Advanced)
        - Machine Learning (Intermediate)
        
        Experience:
        - Software Developer Intern (6 months)
        - Research Assistant in AI lab
        
        Languages: Spanish (Native), English (Fluent)
        
        Interests: Artificial Intelligence, Web Development, Startups
        Ambitions: Work at a top tech company in Silicon Valley or Europe
        """
        
        brain_dump_text = "Quiero una beca o pasantía en Europa o USA para aprender más sobre IA"
        
        print("🔄 Buscando oportunidades...")
        print(f"   CV length: {len(cv_raw_text)} chars")
        print(f"   Brain dump: '{brain_dump_text[:50]}...'")
        
        opportunities = search_opportunities_with_gemini(
            cv_raw_text=cv_raw_text,
            brain_dump_text=brain_dump_text,
            profile_data=None,
            num_results=3
        )
        
        print(f"✅ Se encontraron {len(opportunities)} oportunidades\n")
        
        for i, opp in enumerate(opportunities, 1):
            print(f"{i}. {opp.get('title', 'N/A')}")
            print(f"   Company: {opp.get('company', 'N/A')}")
            print(f"   Type: {opp.get('opportunity_type', 'N/A')}")
            print(f"   Location: {opp.get('location', 'N/A')}")
            print(f"   URL: {opp.get('url', 'N/A')}")
            print(f"   Deadline: {opp.get('deadline_info', 'N/A')}")
            print()
        
        return opportunities
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_6_opportunity_scoring():
    """TEST 6: ¿Puntúa bien las oportunidades?"""
    separator("TEST 6: Opportunity Scoring")
    
    try:
        from src.services.hunter import evaluate_match
        
        cv_raw_text = """
        Engineer with Python expertise
        Skills: Python, Django, React, PostgreSQL
        Languages: Spanish, English
        Interests: AI, Startups
        """
        
        opportunities = [
            {
                "title": "AI Research Intern",
                "company": "Google AI",
                "description": "ML research opportunity for undergrads",
                "opportunity_type": "pasantía",
                "eligibility_level": "pregrado"
            },
            {
                "title": "PhD Program in Philosophy",
                "company": "Harvard",
                "description": "Doctoral program in philosophy",
                "opportunity_type": "doctorate",
                "eligibility_level": "doctorado"
            },
            {
                "title": "Web Developer Bootcamp",
                "company": "Coding School",
                "description": "Learn React in 12 weeks",
                "opportunity_type": "training",
                "eligibility_level": "all"
            }
        ]
        
        print("🔄 Evaluando matches...\n")
        
        scores = []
        for opp in opportunities:
            evaluation = evaluate_match(
                cv_raw_text=cv_raw_text,
                brain_dump_text="Interested in AI roles",
                opportunity=opp,
                profile_data={}
            )
            
            title = opp['title']
            score = evaluation['score']
            reason = evaluation['reason'][:60]
            eligible = "✓" if evaluation['is_eligible'] else "✗"
            
            print(f"[{eligible}] {title}")
            print(f"    Score: {score}/100")
            print(f"    Reason: {reason}...")
            print()
            
            scores.append(score)
        
        print(f"✅ Scoring completado")
        print(f"   Scores: {scores}")
        print(f"   Promedio: {sum(scores)/len(scores):.1f}/100")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_7_database_save():
    """TEST 7: ¿Se guarda bien en la base de datos?"""
    separator("TEST 7: Database Save")
    
    try:
        from src.services.db import save_student_profile, _get_supabase_client
        
        # Datos de prueba
        profile_dict = {
            "name": "Test Student",
            "university": "Test University",
            "career": "Computer Science",
            "country": "Test Country",
            "study_level": "pregrado",
            "languages": ["Spanish", "English"],
            "top_skills": ["Python", "React"],
            "interests": ["AI", "Startups"],
            "ambitions": "Work at a tech company"
        }
        
        cv_raw_text = "This is test CV text with some content to verify storage" * 10
        brain_dump_text = "This is test brain dump"
        
        print("💾 Guardando en base de datos...")
        
        saved_row = save_student_profile(
            profile=profile_dict,
            user_id=None,  # Sin user para test
            cv_raw_text=cv_raw_text,
            brain_dump_text=brain_dump_text
        )
        
        if saved_row and saved_row.get('id'):
            student_id = saved_row['id']
            print(f"✅ Guardado exitosamente")
            print(f"   Student ID: {student_id}")
            print(f"   Name: {saved_row.get('name')}")
            print(f"   CV length in DB: {len(saved_row.get('cv_raw_text', ''))} chars")
            print(f"   Brain dump in DB: {len(saved_row.get('brain_dump_text', ''))} chars")
            
            # Verificar que se puede recuperar
            print("\n🔍 Verificando recuperación de datos...")
            supabase = _get_supabase_client()
            verify = supabase.table("students").select("*").eq("id", student_id).execute()
            
            if verify.data and len(verify.data) > 0:
                print(f"✅ Recuperada 1 row de la DB")
                return student_id
            else:
                print(f"❌ No se pudo recuperar de la DB")
                return None
        else:
            print(f"❌ Error al guardar")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_8_full_pipeline():
    """TEST 8: Pipeline completo (Search + Score + Save)"""
    separator("TEST 8: Full Pipeline (Search → Score → Save)")
    
    try:
        from src.services.hunter import find_and_save_matches
        from src.services.db import _get_supabase_client
        
        # Primero necesitamos un student_id
        print("⚠️ Este test requiere un student_id existente en la DB")
        print("   Ejecuta primero TEST 7 para tener un student_id\n")
        
        # Aquí el usuario debe proporcionar el student_id
        student_id = input("Ingresa el student_id (o presiona Enter para saltar): ").strip()
        
        if not student_id:
            print("⏭️ Test saltado")
            return None
        
        print(f"\n🔄 ejecutando pipeline para student_id: {student_id}")
        
        result = find_and_save_matches(student_id=student_id, num_results=3)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return None
        
        print(f"✅ Pipeline completado")
        print(f"   Estudiante: {result.get('student_name', 'Unknown')}")
        print(f"   Oportunidades encontradas: {result.get('opportunities_count', 0)}")
        print(f"   Matches guardados: {result.get('matches_saved', 0)}")
        
        # Verificar matches en DB
        supabase = _get_supabase_client()
        matches = supabase.table("matches").select("*").eq("student_id", student_id).execute()
        
        print(f"\n📊 Matches en la base de datos:")
        for i, match in enumerate(matches.data, 1):
            opp = match.get('opportunity', {})
            score = match.get('score', 0)
            print(f"   {i}. {opp.get('title', 'N/A')} - {score}/100")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Ejecuta todos los tests"""
    print("\n" + "="*60)
    print("  TESTING SUITE - Novo Project")
    print("="*60)
    print("\nEste script testa cada parte del flujo independientemente")
    print("Ejecuta los tests en orden para mejor debugging\n")
    
    tests = [
        ("Gemini Connection", test_1_gemini_connection),
        ("Supabase Connection", test_2_supabase_connection),
        ("CV Extraction", test_3_cv_extraction),
        ("Profile Analysis", test_4_profile_analysis),
        ("Opportunity Search", test_5_opportunity_search),
        ("Opportunity Scoring", test_6_opportunity_scoring),
        ("Database Save", test_7_database_save),
        ("Full Pipeline", test_8_full_pipeline),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        user_input = input(f"\n¿Ejecutar TEST: {test_name}? (s/n): ").strip().lower()
        if user_input == 's':
            result = test_func()
            results[test_name] = "✅ PASS" if result else "❌ FAIL"
        else:
            print(f"⏭️ Saltado")
            results[test_name] = "⏭️ SKIPPED"
    
    # Resumen
    separator("RESUMEN DE RESULTADOS")
    for test_name, result in results.items():
        print(f"{result} - {test_name}")
    print()


if __name__ == "__main__":
    main()
