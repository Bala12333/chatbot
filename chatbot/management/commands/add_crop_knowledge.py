"""
Management command to add expanded crop knowledge base.
"""

from django.core.management.base import BaseCommand
from chatbot.models import KnowledgeBase


class Command(BaseCommand):
    help = 'Add expanded crop knowledge for rice, wheat, corn and more'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--language',
            type=str,
            default='en-US',
            help='Language code for the knowledge base entries'
        )
    
    def handle(self, *args, **options):
        language_code = options['language']
        
        # Expanded crop knowledge data
        expanded_knowledge = {
            'en-US': [
                # Rice Knowledge
                {
                    'category': 'crop_diseases',
                    'topic': 'Rice Blast',
                    'question_patterns': 'rice blast\nrice disease\nrice leaves spots\nrice fungal disease\nblast disease rice',
                    'answer': 'Rice blast is caused by Magnaporthe oryzae fungus. Symptoms include diamond-shaped lesions on leaves with gray centers and brown borders. Neck blast causes panicle breakage. Control: Use resistant varieties, avoid excessive nitrogen, apply fungicides like tricyclazole, maintain proper water management.'
                },
                {
                    'category': 'crop_diseases',
                    'topic': 'Rice Brown Spot',
                    'question_patterns': 'rice brown spot\nbrown spot rice\nrice leaf brown\nbipolaris oryzae\nrice seedling disease',
                    'answer': 'Brown spot is caused by Bipolaris oryzae. Circular to oval brown spots on leaves, often with yellow halos. Common in nutrient-deficient fields. Control: Balanced fertilization especially potassium, seed treatment with fungicides, crop rotation, remove infected debris.'
                },
                {
                    'category': 'fertilizer_recommendations',
                    'topic': 'Rice Fertilizer Program',
                    'question_patterns': 'rice fertilizer\nrice nutrition\nfertilizer for rice\nrice NPK\npaddy fertilizer',
                    'answer': 'Rice fertilizer program: Basal application - 40-60 kg N + 40-60 kg P2O5 + 40 kg K2O per hectare. Top dressing: 30-40 kg N at tillering, 20-30 kg N at panicle initiation. Use urea for nitrogen, DAP/SSP for phosphorus, MOP for potassium. Adjust based on soil test.'
                },
                
                # Wheat Knowledge
                {
                    'category': 'crop_diseases',
                    'topic': 'Wheat Stripe Rust',
                    'question_patterns': 'wheat stripe rust\nyellow rust wheat\nwheat rust stripes\npuccinia striiformis\nwheat yellow stripes',
                    'answer': 'Stripe rust (yellow rust) caused by Puccinia striiformis appears as yellow stripes on leaves parallel to veins. Thrives in cool, moist conditions. Control: Plant resistant varieties, apply fungicides (propiconazole, tebuconazole) at first sign, avoid late planting, remove volunteer wheat.'
                },
                {
                    'category': 'crop_diseases',
                    'topic': 'Wheat Powdery Mildew',
                    'question_patterns': 'wheat powdery mildew\nwhite powder wheat\nwheat leaves white\nblumeria graminis\nwheat fungal white',
                    'answer': 'Powdery mildew appears as white powdery patches on leaves and stems. Caused by Blumeria graminis. Reduces photosynthesis and grain quality. Control: Plant resistant varieties, ensure good air circulation, apply sulfur-based fungicides, avoid excessive nitrogen.'
                },
                {
                    'category': 'fertilizer_recommendations',
                    'topic': 'Wheat Fertilizer Schedule',
                    'question_patterns': 'wheat fertilizer\nwheat nutrition\nfertilizer for wheat\nwheat NPK\nwheat nutrients',
                    'answer': 'Wheat fertilizer program: Apply 80-120 kg N, 40-60 kg P2O5, 40 kg K2O per hectare. Split nitrogen: 1/3 at sowing, 1/3 at tillering (21 DAS), 1/3 at stem elongation (45 DAS). Use urea for nitrogen, DAP for phosphorus. Add zinc sulfate 25 kg/ha if deficient.'
                },
                
                # Corn Knowledge
                {
                    'category': 'crop_diseases',
                    'topic': 'Corn Borer',
                    'question_patterns': 'corn borer\nmaize borer\ncorn worms\nstalk borer corn\nostrinia nubilalis\ncorn stem borer',
                    'answer': 'European corn borer larvae tunnel into stalks and ears. Signs include shot holes in leaves, broken tassels, sawdust-like frass. Control: Plant Bt corn varieties, apply insecticides (chlorantraniliprole) during egg laying, destroy crop residues, use pheromone traps for monitoring.'
                },
                {
                    'category': 'crop_diseases',
                    'topic': 'Corn Leaf Blight',
                    'question_patterns': 'corn leaf blight\nmaize leaf blight\ncorn northern blight\nsetosphaeria turcica\ncorn gray leaf spot',
                    'answer': 'Northern corn leaf blight causes long grayish lesions on leaves. Southern blight shows smaller spots with halos. Control: Plant resistant hybrids, crop rotation with non-grass crops, apply fungicides (strobilurin, triazole), manage crop residue, ensure proper plant spacing.'
                },
                {
                    'category': 'fertilizer_recommendations',
                    'topic': 'Corn Nutrition Program',
                    'question_patterns': 'corn fertilizer\nmaize fertilizer\ncorn nutrition\nfertilizer for corn\ncorn NPK requirements',
                    'answer': 'Corn fertilizer program: Apply 150-200 kg N, 60-80 kg P2O5, 40-60 kg K2O per hectare. Split nitrogen: 25% at planting, 50% at V6 stage (side-dress), 25% at tasseling. Include micronutrients: zinc 5 kg/ha, boron 1 kg/ha. Use soil test for precise recommendations.'
                },
                
                # General Crop Management
                {
                    'category': 'general',
                    'topic': 'Crop Rotation Benefits',
                    'question_patterns': 'crop rotation\nrotation benefits\ncrop sequence\nrotation farming\nrotational cropping',
                    'answer': 'Crop rotation benefits: Breaks pest and disease cycles, improves soil fertility, reduces herbicide resistance, enhances soil structure. Good rotations: Cereal-legume-root crop, rice-wheat-mung bean. Include cover crops, avoid same family crops consecutively, plan 3-4 year rotations.'
                },
                {
                    'category': 'pest_identification',
                    'topic': 'Armyworm Control',
                    'question_patterns': 'armyworm\nfall armyworm\narcmy worm\nspodoptera frugiperda\ncorn armyworm\narmyworm control',
                    'answer': 'Fall armyworm affects corn, rice, sorghum. Larvae feed on leaves creating characteristic window-pane damage. Control: Early detection with pheromone traps, apply Bt sprays or synthetic insecticides (emamectin benzoate), encourage natural enemies, plant trap crops like napier grass.'
                },
                {
                    'category': 'weather_advice',
                    'topic': 'Heat Stress Management',
                    'question_patterns': 'heat stress crops\nhot weather farming\ncrop heat damage\nhigh temperature crops\nheat wave agriculture',
                    'answer': 'Heat stress reduces yields and quality. Management: Choose heat-tolerant varieties, provide shade nets (25-35%), mulch soil to reduce temperature, irrigate during early morning/evening, apply anti-transpirants, ensure adequate potassium nutrition, harvest early morning.'
                }
            ],
            'es-ES': [
                {
                    'category': 'crop_diseases',
                    'topic': 'Añublo del Arroz',
                    'question_patterns': 'añublo arroz\nenfermedad arroz\narroz manchas hojas\nhongo arroz\nblast arroz',
                    'answer': 'El añublo del arroz es causado por el hongo Magnaporthe oryzae. Los síntomas incluyen lesiones en forma de diamante en las hojas con centros grises y bordes marrones. Control: Usar variedades resistentes, evitar exceso de nitrógeno, aplicar fungicidas como tricyclazole.'
                },
                {
                    'category': 'crop_diseases', 
                    'topic': 'Roya del Trigo',
                    'question_patterns': 'roya trigo\nroya amarilla\ntrigo rayas amarillas\npuccinia striiformis\ntrigo hongos',
                    'answer': 'La roya amarilla del trigo aparece como rayas amarillas en las hojas paralelas a las venas. Control: Plantar variedades resistentes, aplicar fungicidas (propiconazol, tebuconazol) al primer síntoma, evitar siembra tardía, eliminar trigo voluntario.'
                },
                {
                    'category': 'fertilizer_recommendations',
                    'topic': 'Fertilización del Maíz',
                    'question_patterns': 'fertilizante maíz\nnutrición maíz\nfertilizar maíz\nNPK maíz\nnutrientes maíz',
                    'answer': 'Programa de fertilización del maíz: Aplicar 150-200 kg N, 60-80 kg P2O5, 40-60 kg K2O por hectárea. Dividir nitrógeno: 25% en siembra, 50% en V6, 25% en floración. Incluir micronutrientes: zinc 5 kg/ha, boro 1 kg/ha.'
                }
            ],
            'hi-IN': [
                {
                    'category': 'crop_diseases',
                    'topic': 'चावल का ब्लास्ट रोग',
                    'question_patterns': 'चावल ब्लास्ट\nधान रोग\nचावल पत्ती धब्बे\nधान फफूंद रोग\nब्लास्ट रोग',
                    'answer': 'चावल का ब्लास्ट रोग Magnaporthe oryzae कवक से होता है। पत्तियों पर हीरे के आकार के धब्बे दिखते हैं। नियंत्रण: प्रतिरोधी किस्में लगाएं, अधिक नाइट्रोजन से बचें, ट्राइसाइक्लाज़ोल जैसे फफूंदनाशी का छिड़काव करें।'
                },
                {
                    'category': 'crop_diseases',
                    'topic': 'गेहूं का पीला रतुआ',
                    'question_patterns': 'गेहूं रतुआ\nपीला रतुआ\nगेहूं पीली धारियां\nगेहूं फफूंद\nरतुआ रोग',
                    'answer': 'गेहूं का पीला रतुआ पत्तियों पर पीली धारियों के रूप में दिखता है। नियंत्रण: प्रतिरोधी किस्में लगाएं, पहले लक्षण पर फफूंदनाशी छिड़कें, देर से बुआई न करें, स्वयंजात गेहूं हटाएं।'
                },
                {
                    'category': 'fertilizer_recommendations',
                    'topic': 'मक्का में खाद',
                    'question_patterns': 'मक्का खाद\nमक्का उर्वरक\nमक्का पोषण\nमक्का NPK\nमक्का पोषक तत्व',
                    'answer': 'मक्का उर्वरक कार्यक्रम: 150-200 किग्रा नाइट्रोजन, 60-80 किग्रा फास्फोरस, 40-60 किग्रा पोटाश प्रति हेक्टेयर। नाइट्रोजन बांटें: 25% बुआई पर, 50% V6 अवस्था में, 25% फूल आने पर। सूक्ष्म पोषक तत्व: जिंक 5 किग्रा/हेक्टेयर।'
                }
            ]
        }
        
        # Get data for the specified language, fallback to English if not available
        data = expanded_knowledge.get(language_code, expanded_knowledge['en-US'])
        
        self.stdout.write(f'Adding expanded crop knowledge with {len(data)} entries for language: {language_code}')
        
        created_count = 0
        updated_count = 0
        
        for entry in data:
            knowledge_entry, created = KnowledgeBase.objects.get_or_create(
                category=entry['category'],
                topic=entry['topic'],
                language_code=language_code,
                defaults={
                    'question_patterns': entry['question_patterns'],
                    'answer': entry['answer']
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(f'Created: {knowledge_entry.topic}')
            else:
                # Update existing entry
                knowledge_entry.question_patterns = entry['question_patterns']
                knowledge_entry.answer = entry['answer']
                knowledge_entry.save()
                updated_count += 1
                self.stdout.write(f'Updated: {knowledge_entry.topic}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully added expanded crop knowledge: {created_count} created, {updated_count} updated'
            )
        )