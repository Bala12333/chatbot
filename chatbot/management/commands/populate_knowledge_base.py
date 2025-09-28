"""
Management command to populate the knowledge base with sample agricultural data.
"""

from django.core.management.base import BaseCommand
from chatbot.models import KnowledgeBase


class Command(BaseCommand):
    help = 'Populate the knowledge base with sample agricultural data'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--language',
            type=str,
            default='en-US',
            help='Language code for the knowledge base entries'
        )
    
    def handle(self, *args, **options):
        language_code = options['language']
        
        # Sample knowledge base data
        knowledge_data = {
            'en-US': [
                {
                    'category': 'crop_diseases',
                    'topic': 'Tomato Blight',
                    'question_patterns': 'tomato blight\ntomato disease\ntomato leaves turning brown\ntomato plant dying',
                    'answer': 'Tomato blight is caused by fungal pathogens. Early blight shows brown spots with concentric rings on leaves. Late blight causes dark, water-soaked lesions. Treatment: Remove affected leaves, improve air circulation, apply copper-based fungicides, avoid overhead watering.'
                },
                {
                    'category': 'crop_diseases',
                    'topic': 'Wheat Rust',
                    'question_patterns': 'wheat rust\nwheat orange spots\nwheat fungal disease\nwheat leaves yellow',
                    'answer': 'Wheat rust appears as orange or reddish-brown pustules on leaves and stems. It\'s caused by fungal spores spread by wind. Prevention: Plant resistant varieties, apply fungicides preventively, remove crop residue, practice crop rotation.'
                },
                {
                    'category': 'pest_identification',
                    'topic': 'Aphids',
                    'question_patterns': 'aphids\ngreen bugs on plants\nsmall insects on leaves\nsticky honeydew on plants',
                    'answer': 'Aphids are small, soft-bodied insects that cluster on new growth and undersides of leaves. They secrete sticky honeydew. Control: Spray with water, introduce beneficial insects like ladybugs, use insecticidal soap, neem oil, or systemic insecticides for severe infestations.'
                },
                {
                    'category': 'pest_identification',
                    'topic': 'Caterpillars',
                    'question_patterns': 'caterpillars\nworms eating leaves\nleaves with holes\ngreen worms on plants',
                    'answer': 'Caterpillars are larvae of moths and butterflies that chew irregular holes in leaves. Common types include armyworms, cutworms, and cabbage worms. Control: Hand-picking, Bt (Bacillus thuringiensis) spray, beneficial nematodes, or appropriate insecticides.'
                },
                {
                    'category': 'fertilizer_recommendations',
                    'topic': 'Nitrogen Deficiency',
                    'question_patterns': 'yellow leaves\nnitrogen deficiency\nplant growth slow\nleaves turning pale',
                    'answer': 'Nitrogen deficiency causes yellowing of older leaves, stunted growth, and poor fruit development. Solutions: Apply nitrogen-rich fertilizers like urea (46-0-0), ammonium sulfate, or compost. For vegetables: 1-2 lbs nitrogen per 1000 sq ft. Monitor soil pH (6.0-7.0 optimal).'
                },
                {
                    'category': 'fertilizer_recommendations',
                    'topic': 'Phosphorus for Root Development',
                    'question_patterns': 'phosphorus fertilizer\nroot development\npoor flowering\nseedling growth',
                    'answer': 'Phosphorus promotes root development, flowering, and seed formation. Deficiency shows as purple leaf tinges and poor root growth. Apply bone meal, rock phosphate, or balanced fertilizers (10-10-10). Best applied at planting time as phosphorus moves slowly in soil.'
                },
                {
                    'category': 'soil_health',
                    'topic': 'Soil pH Management',
                    'question_patterns': 'soil pH\nacidic soil\nbasic soil\nsoil testing\nlime application',
                    'answer': 'Most crops prefer pH 6.0-7.0. Test soil annually. To raise pH (acidic soil): Add agricultural lime 2-4 months before planting. To lower pH (alkaline soil): Add sulfur, peat moss, or organic matter. Apply changes gradually over multiple seasons.'
                },
                {
                    'category': 'soil_health',
                    'topic': 'Organic Matter Benefits',
                    'question_patterns': 'organic matter\ncompost\nsoil improvement\nsoil structure\nwater retention',
                    'answer': 'Organic matter improves soil structure, water retention, and nutrient availability. Add 2-4 inches of compost annually. Benefits include better drainage in clay soils, increased water retention in sandy soils, and gradual nutrient release for plants.'
                },
                {
                    'category': 'weather_advice',
                    'topic': 'Frost Protection',
                    'question_patterns': 'frost protection\ncold weather\nfreezing temperatures\nplant protection winter',
                    'answer': 'Protect plants from frost with: Row covers, mulching around base, bringing potted plants indoors, watering before frost (wet soil retains heat), using frost blankets, or setting up wind barriers. Harvest tender crops before first expected frost.'
                },
                {
                    'category': 'weather_advice',
                    'topic': 'Drought Management',
                    'question_patterns': 'drought\nwater shortage\ndry conditions\nwatering plants\nwater conservation',
                    'answer': 'During drought: Deep, infrequent watering is better than frequent shallow watering. Apply mulch to retain moisture, choose drought-tolerant varieties, install drip irrigation, collect rainwater, and water early morning to reduce evaporation.'
                }
            ],
            'es-ES': [
                {
                    'category': 'crop_diseases',
                    'topic': 'Tizón del Tomate',
                    'question_patterns': 'tizón tomate\nenfermedad tomate\nhojas tomate marrones\nplanta tomate muriendo',
                    'answer': 'El tizón del tomate es causado por patógenos fúngicos. El tizón temprano muestra manchas marrones con anillos concéntricos en las hojas. El tizón tardío causa lesiones oscuras empapadas de agua. Tratamiento: Remover hojas afectadas, mejorar circulación del aire, aplicar fungicidas de cobre, evitar riego por aspersión.'
                },
                {
                    'category': 'pest_identification',
                    'topic': 'Pulgones',
                    'question_patterns': 'pulgones\ninsectos verdes plantas\ninsectos pequeños hojas\nmelaza pegajosa plantas',
                    'answer': 'Los pulgones son insectos pequeños de cuerpo blando que se agrupan en brotes nuevos y el envés de las hojas. Secretan melaza pegajosa. Control: Rociar con agua, introducir insectos beneficiosos como mariquitas, usar jabón insecticida, aceite de neem, o insecticidas sistémicos para infestaciones severas.'
                },
                {
                    'category': 'fertilizer_recommendations',
                    'topic': 'Deficiencia de Nitrógeno',
                    'question_patterns': 'hojas amarillas\ndeficiencia nitrógeno\ncrecimiento planta lento\nhojas pálidas',
                    'answer': 'La deficiencia de nitrógeno causa amarillamiento de hojas viejas, crecimiento atrofiado y mal desarrollo de frutos. Soluciones: Aplicar fertilizantes ricos en nitrógeno como urea (46-0-0), sulfato de amonio, o compost. Para vegetales: 1-2 libras de nitrógeno por 1000 pies cuadrados.'
                }
            ],
            'hi-IN': [
                {
                    'category': 'crop_diseases',
                    'topic': 'टमाटर का झुलसा रोग',
                    'question_patterns': 'टमाटर झुलसा\nटमाटर रोग\nटमाटर पत्ते भूरे\nटमाटर पौधा मरना',
                    'answer': 'टमाटर का झुलसा रोग कवक रोगजनकों से होता है। प्रारंभिक झुलसा पत्तियों पर भूरे धब्बे दिखाता है। देर से झुलसा काले, पानी से भीगे हुए घाव बनाता है। उपचार: प्रभावित पत्तियों को हटाएं, हवा का संचार बेहतर करें, तांबा आधारित कवकनाशी लगाएं।'
                },
                {
                    'category': 'pest_identification',
                    'topic': 'माहू कीट',
                    'question_patterns': 'माहू\nपौधों पर हरे कीड़े\nपत्तियों पर छोटे कीड़े\nपौधों पर चिपचिपा द्रव',
                    'answer': 'माहू छोटे, मुलायम शरीर वाले कीड़े हैं जो नई पत्तियों और पत्तियों के नीचे समूह बनाते हैं। ये चिपचिपा शहद स्रावित करते हैं। नियंत्रण: पानी से छिड़काव, लेडीबग जैसे लाभकारी कीड़े लाएं, कीटनाशक साबुन का उपयोग करें।'
                }
            ]
        }
        
        # Get data for the specified language, fallback to English if not available
        data = knowledge_data.get(language_code, knowledge_data['en-US'])
        
        self.stdout.write(f'Populating knowledge base with {len(data)} entries for language: {language_code}')
        
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
                f'Successfully populated knowledge base: {created_count} created, {updated_count} updated'
            )
        )