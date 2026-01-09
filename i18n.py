"""
Internationalization module with auto-language detection.
Provides multi-language support for the bot.
"""

import logging
from typing import Dict, Optional
from langdetect import detect, LangDetectException

logger = logging.getLogger(__name__)


class I18n:
    """Handles internationalization and auto-language detection."""
    
    # Language translations
    TRANSLATIONS = {
        'en': {
            'welcome': (
                "👋 Welcome to YouTube Thumbnail Extractor!\n\n"
                "Send me any YouTube link or video ID, and I'll send you all available thumbnails.\n\n"
                "📝 Commands:\n"
                "/start - Start the bot\n"
                "/help - Show help\n"
                "/stats - Your statistics\n"
                "/referral - Get your referral link\n"
                "/premium - Premium info\n"
                "/language - Change language"
            ),
            'welcome_referred': (
                "👋 Welcome! You were referred by user {referrer_id}.\n"
                "You both get {bonus} bonus requests! 🎁\n\n"
                "Send me any YouTube link or video ID to get started."
            ),
            'help': (
                "🔍 How to use:\n\n"
                "1. Send me a YouTube link in any format:\n"
                "   • youtube.com/watch?v=VIDEO_ID\n"
                "   • youtu.be/VIDEO_ID\n"
                "   • youtube.com/shorts/VIDEO_ID\n"
                "   • Or just the video ID\n\n"
                "2. I'll send you all available thumbnails!\n\n"
                "💎 Premium features:\n"
                "• Higher daily limits\n"
                "• Priority processing\n"
                "• No ads\n\n"
                "Use /premium to upgrade!"
            ),
            'stats': (
                "📊 Your Statistics:\n\n"
                "Daily requests used: {used}/{limit}\n"
                "Total referrals: {referrals}\n"
                "Premium status: {premium}\n"
                "Member since: {joined}"
            ),
            'referral_info': (
                "🎁 Referral Program:\n\n"
                "Share your link and earn bonuses!\n"
                "Each referral gives you {bonus} extra requests.\n"
                "Get {required} referrals for free premium! 💎\n\n"
                "Your referral link:\n{link}\n\n"
                "Total referrals: {count}"
            ),
            'premium_info': (
                "💎 Premium Benefits:\n\n"
                "✅ {premium_limit} requests per day\n"
                "✅ Priority processing\n"
                "✅ No ads\n"
                "✅ Early access to new features\n\n"
                "🎁 Get premium FREE by referring {required} users!\n"
                "Use /referral to get your link.\n\n"
                "Current referrals: {count}/{required}"
            ),
            'processing': "⏳ Processing your request...",
            'thumbnails_found': "✅ Found {count} thumbnails for video: {video_id}",
            'no_thumbnails': "❌ No thumbnails found for this video.",
            'invalid_link': "❌ Invalid YouTube link or video ID. Please try again.",
            'limit_reached': (
                "⚠️ Daily limit reached ({limit} requests).\n"
                "Upgrade to premium for {premium_limit} requests per day!\n"
                "Or refer friends to get bonus requests: /referral"
            ),
            'flood_warning': "⚠️ Please slow down! Wait {seconds} seconds before trying again.",
            'error': "❌ An error occurred. Please try again later.",
            'premium_granted': "🎉 Congratulations! You've earned premium status! 💎",
            'language_changed': "✅ Language changed to: {language}",
            'choose_language': "🌍 Choose your language:",
            'yes': "Yes ✅",
            'no': "No ❌",
            'main_menu': "🏠 Main Menu\n\nChoose an option below:",
            'what_next': "✅ Done! What would you like to do next?",
            'send_video_link': "📹 Send me a YouTube link or video ID!",
            'user_banned': "🚫 You have been banned from using this bot.",
            'payment_options': (
                "💳 Payment Options:\n\n"
                "Choose your preferred payment method to upgrade to premium:"
            ),
            'upi_payment_instructions': (
                "💰 UPI Payment Instructions:\n\n"
                "1. Send payment to UPI ID: {upi_id}\n"
                "2. Take a screenshot of the payment confirmation\n"
                "3. Upload the screenshot here\n"
                "4. Wait for admin approval\n\n"
                "Price: Check with admin for current pricing"
            ),
            'stars_payment_coming_soon': "⭐ Telegram Stars payment coming soon!",
            'send_payment_screenshot': (
                "📸 Please send your payment screenshot.\n\n"
                "Make sure the screenshot clearly shows the transaction details."
            ),
            'payment_proof_received': (
                "✅ Payment proof received!\n\n"
                "Your payment is under review. You'll be notified once approved."
            ),
            'payment_approved': (
                "🎉 Congratulations!\n\n"
                "Your payment has been approved!\n"
                "You now have premium access for {days} days. Enjoy! 💎"
            ),
            'payment_rejected': (
                "❌ Payment Rejected\n\n"
                "Your payment proof was rejected. Please contact admin for details."
            ),
            # Button texts
            'btn_help': "❓ Help",
            'btn_stats': "📊 My Stats",
            'btn_referral': "🎁 Referral",
            'btn_premium': "💎 Premium",
            'btn_buy_premium': "💳 Buy Premium",
            'btn_upgrade_premium': "⬆️ Upgrade to Premium",
            'btn_main_menu': "🏠 Main Menu",
            'btn_new_video': "🆕 New Video",
            'btn_upi_payment': "💰 UPI Payment (India)",
            'btn_stars_payment': "⭐ Telegram Stars",
            'btn_back': "⬅️ Back",
            'btn_upload_proof': "📸 Upload Payment Proof",
        },
        'es': {
            'welcome': (
                "👋 ¡Bienvenido al Extractor de Miniaturas de YouTube!\n\n"
                "Envíame cualquier enlace de YouTube o ID de video, y te enviaré todas las miniaturas disponibles.\n\n"
                "📝 Comandos:\n"
                "/start - Iniciar el bot\n"
                "/help - Mostrar ayuda\n"
                "/stats - Tus estadísticas\n"
                "/referral - Obtener tu enlace de referido\n"
                "/premium - Información premium\n"
                "/language - Cambiar idioma"
            ),
            'welcome_referred': (
                "👋 ¡Bienvenido! Fuiste referido por el usuario {referrer_id}.\n"
                "¡Ambos reciben {bonus} solicitudes de bonificación! 🎁\n\n"
                "Envíame cualquier enlace de YouTube para comenzar."
            ),
            'help': (
                "🔍 Cómo usar:\n\n"
                "1. Envíame un enlace de YouTube en cualquier formato:\n"
                "   • youtube.com/watch?v=VIDEO_ID\n"
                "   • youtu.be/VIDEO_ID\n"
                "   • youtube.com/shorts/VIDEO_ID\n"
                "   • O solo el ID del video\n\n"
                "2. ¡Te enviaré todas las miniaturas disponibles!\n\n"
                "💎 Características premium:\n"
                "• Límites diarios más altos\n"
                "• Procesamiento prioritario\n"
                "• Sin anuncios\n\n"
                "¡Usa /premium para actualizar!"
            ),
            'stats': (
                "📊 Tus Estadísticas:\n\n"
                "Solicitudes diarias usadas: {used}/{limit}\n"
                "Referidos totales: {referrals}\n"
                "Estado premium: {premium}\n"
                "Miembro desde: {joined}"
            ),
            'referral_info': (
                "🎁 Programa de Referidos:\n\n"
                "¡Comparte tu enlace y gana bonificaciones!\n"
                "Cada referido te da {bonus} solicitudes extra.\n"
                "¡Consigue {required} referidos para premium gratis! 💎\n\n"
                "Tu enlace de referido:\n{link}\n\n"
                "Referidos totales: {count}"
            ),
            'premium_info': (
                "💎 Beneficios Premium:\n\n"
                "✅ {premium_limit} solicitudes por día\n"
                "✅ Procesamiento prioritario\n"
                "✅ Sin anuncios\n"
                "✅ Acceso anticipado a nuevas funciones\n\n"
                "🎁 ¡Obtén premium GRATIS refiriendo {required} usuarios!\n"
                "Usa /referral para obtener tu enlace.\n\n"
                "Referidos actuales: {count}/{required}"
            ),
            'processing': "⏳ Procesando tu solicitud...",
            'thumbnails_found': "✅ Se encontraron {count} miniaturas para el video: {video_id}",
            'no_thumbnails': "❌ No se encontraron miniaturas para este video.",
            'invalid_link': "❌ Enlace o ID de YouTube inválido. Por favor, inténtalo de nuevo.",
            'limit_reached': (
                "⚠️ Límite diario alcanzado ({limit} solicitudes).\n"
                "¡Actualiza a premium para {premium_limit} solicitudes por día!\n"
                "O refiere amigos para obtener solicitudes de bonificación: /referral"
            ),
            'flood_warning': "⚠️ ¡Por favor, ve más despacio! Espera {seconds} segundos antes de intentarlo de nuevo.",
            'error': "❌ Ocurrió un error. Por favor, inténtalo de nuevo más tarde.",
            'premium_granted': "🎉 ¡Felicitaciones! ¡Has obtenido el estado premium! 💎",
            'language_changed': "✅ Idioma cambiado a: {language}",
            'choose_language': "🌍 Elige tu idioma:",
            'yes': "Sí ✅",
            'no': "No ❌",
            'main_menu': "🏠 Menú Principal\n\nElige una opción a continuación:",
            'what_next': "✅ ¡Hecho! ¿Qué te gustaría hacer a continuación?",
            'send_video_link': "📹 ¡Envíame un enlace de YouTube o ID de video!",
            'user_banned': "🚫 Has sido baneado de usar este bot.",
            'payment_options': (
                "💳 Opciones de Pago:\n\n"
                "Elige tu método de pago preferido para actualizar a premium:"
            ),
            'upi_payment_instructions': (
                "💰 Instrucciones de Pago UPI:\n\n"
                "1. Envía el pago a UPI ID: {upi_id}\n"
                "2. Toma una captura de pantalla de la confirmación de pago\n"
                "3. Sube la captura de pantalla aquí\n"
                "4. Espera la aprobación del administrador\n\n"
                "Precio: Consulta con el administrador el precio actual"
            ),
            'stars_payment_coming_soon': "⭐ ¡Pago con Telegram Stars próximamente!",
            'send_payment_screenshot': (
                "📸 Por favor, envía tu captura de pantalla de pago.\n\n"
                "Asegúrate de que la captura muestre claramente los detalles de la transacción."
            ),
            'payment_proof_received': (
                "✅ ¡Prueba de pago recibida!\n\n"
                "Tu pago está en revisión. Se te notificará una vez aprobado."
            ),
            'payment_approved': (
                "🎉 ¡Felicitaciones!\n\n"
                "¡Tu pago ha sido aprobado!\n"
                "Ahora tienes acceso premium por {days} días. ¡Disfruta! 💎"
            ),
            'payment_rejected': (
                "❌ Pago Rechazado\n\n"
                "Tu prueba de pago fue rechazada. Por favor contacta al administrador para detalles."
            ),
            # Button texts
            'btn_help': "❓ Ayuda",
            'btn_stats': "📊 Mis Estadísticas",
            'btn_referral': "🎁 Referidos",
            'btn_premium': "💎 Premium",
            'btn_buy_premium': "💳 Comprar Premium",
            'btn_upgrade_premium': "⬆️ Actualizar a Premium",
            'btn_main_menu': "🏠 Menú Principal",
            'btn_new_video': "🆕 Nuevo Video",
            'btn_upi_payment': "💰 Pago UPI (India)",
            'btn_stars_payment': "⭐ Telegram Stars",
            'btn_back': "⬅️ Volver",
            'btn_upload_proof': "📸 Subir Prueba de Pago",
        },
        'hi': {
            'welcome': (
                "👋 YouTube थंबनेल एक्सट्रैक्टर में आपका स्वागत है!\n\n"
                "मुझे कोई भी YouTube लिंक या वीडियो ID भेजें, और मैं आपको सभी उपलब्ध थंबनेल भेज दूंगा।\n\n"
                "📝 कमांड:\n"
                "/start - बॉट शुरू करें\n"
                "/help - मदद दिखाएं\n"
                "/stats - आपके आंकड़े\n"
                "/referral - अपना रेफरल लिंक प्राप्त करें\n"
                "/premium - प्रीमियम जानकारी\n"
                "/language - भाषा बदलें"
            ),
            'welcome_referred': (
                "👋 स्वागत है! आपको उपयोगकर्ता {referrer_id} द्वारा रेफर किया गया था।\n"
                "आप दोनों को {bonus} बोनस अनुरोध मिलते हैं! 🎁\n\n"
                "शुरू करने के लिए मुझे कोई भी YouTube लिंक भेजें।"
            ),
            'help': (
                "🔍 उपयोग कैसे करें:\n\n"
                "1. मुझे किसी भी प्रारूप में YouTube लिंक भेजें:\n"
                "   • youtube.com/watch?v=VIDEO_ID\n"
                "   • youtu.be/VIDEO_ID\n"
                "   • youtube.com/shorts/VIDEO_ID\n"
                "   • या बस वीडियो ID\n\n"
                "2. मैं आपको सभी उपलब्ध थंबनेल भेज दूंगा!\n\n"
                "💎 प्रीमियम सुविधाएं:\n"
                "• उच्च दैनिक सीमा\n"
                "• प्राथमिकता प्रसंस्करण\n"
                "• कोई विज्ञापन नहीं\n\n"
                "अपग्रेड करने के लिए /premium का उपयोग करें!"
            ),
            'stats': (
                "📊 आपके आंकड़े:\n\n"
                "दैनिक अनुरोध उपयोग किए गए: {used}/{limit}\n"
                "कुल रेफरल: {referrals}\n"
                "प्रीमियम स्थिति: {premium}\n"
                "सदस्य बने: {joined}"
            ),
            'referral_info': (
                "🎁 रेफरल प्रोग्राम:\n\n"
                "अपना लिंक साझा करें और बोनस कमाएं!\n"
                "प्रत्येक रेफरल आपको {bonus} अतिरिक्त अनुरोध देता है।\n"
                "मुफ्त प्रीमियम के लिए {required} रेफरल प्राप्त करें! 💎\n\n"
                "आपका रेफरल लिंक:\n{link}\n\n"
                "कुल रेफरल: {count}"
            ),
            'premium_info': (
                "💎 प्रीमियम लाभ:\n\n"
                "✅ प्रति दिन {premium_limit} अनुरोध\n"
                "✅ प्राथमिकता प्रसंस्करण\n"
                "✅ कोई विज्ञापन नहीं\n"
                "✅ नई सुविधाओं तक जल्दी पहुंच\n\n"
                "🎁 {required} उपयोगकर्ताओं को रेफर करके मुफ्त में प्रीमियम प्राप्त करें!\n"
                "अपना लिंक प्राप्त करने के लिए /referral का उपयोग करें।\n\n"
                "वर्तमान रेफरल: {count}/{required}"
            ),
            'processing': "⏳ आपके अनुरोध को संसाधित किया जा रहा है...",
            'thumbnails_found': "✅ वीडियो के लिए {count} थंबनेल मिले: {video_id}",
            'no_thumbnails': "❌ इस वीडियो के लिए कोई थंबनेल नहीं मिला।",
            'invalid_link': "❌ अमान्य YouTube लिंक या वीडियो ID। कृपया पुनः प्रयास करें।",
            'limit_reached': (
                "⚠️ दैनिक सीमा पूर्ण ({limit} अनुरोध)।\n"
                "प्रति दिन {premium_limit} अनुरोधों के लिए प्रीमियम में अपग्रेड करें!\n"
                "या बोनस अनुरोध प्राप्त करने के लिए दोस्तों को रेफर करें: /referral"
            ),
            'flood_warning': "⚠️ कृपया धीमे हों! पुनः प्रयास करने से पहले {seconds} सेकंड प्रतीक्षा करें।",
            'error': "❌ एक त्रुटि हुई। कृपया बाद में पुनः प्रयास करें।",
            'premium_granted': "🎉 बधाई हो! आपने प्रीमियम स्थिति अर्जित की है! 💎",
            'language_changed': "✅ भाषा बदल गई: {language}",
            'choose_language': "🌍 अपनी भाषा चुनें:",
            'yes': "हाँ ✅",
            'no': "नहीं ❌",
            'main_menu': "🏠 मुख्य मेनू\n\nनीचे से एक विकल्प चुनें:",
            'what_next': "✅ हो गया! आप आगे क्या करना चाहेंगे?",
            'send_video_link': "📹 मुझे YouTube लिंक या वीडियो ID भेजें!",
            'user_banned': "🚫 आपको इस बॉट का उपयोग करने से प्रतिबंधित कर दिया गया है।",
            'payment_options': (
                "💳 भुगतान विकल्प:\n\n"
                "प्रीमियम में अपग्रेड करने के लिए अपनी पसंदीदा भुगतान विधि चुनें:"
            ),
            'upi_payment_instructions': (
                "💰 UPI भुगतान निर्देश:\n\n"
                "1. UPI ID पर भुगतान भेजें: {upi_id}\n"
                "2. भुगतान पुष्टि का स्क्रीनशॉट लें\n"
                "3. स्क्रीनशॉट यहां अपलोड करें\n"
                "4. व्यवस्थापक की स्वीकृति की प्रतीक्षा करें\n\n"
                "कीमत: वर्तमान मूल्य के लिए व्यवस्थापक से जांचें"
            ),
            'stars_payment_coming_soon': "⭐ Telegram Stars भुगतान जल्द आ रहा है!",
            'send_payment_screenshot': (
                "📸 कृपया अपना भुगतान स्क्रीनशॉट भेजें।\n\n"
                "सुनिश्चित करें कि स्क्रीनशॉट में लेनदेन विवरण स्पष्ट रूप से दिखाई दे रहे हैं।"
            ),
            'payment_proof_received': (
                "✅ भुगतान प्रमाण प्राप्त हुआ!\n\n"
                "आपका भुगतान समीक्षाधीन है। स्वीकृत होने पर आपको सूचित किया जाएगा।"
            ),
            'payment_approved': (
                "🎉 बधाई हो!\n\n"
                "आपका भुगतान स्वीकृत हो गया है!\n"
                "अब आपके पास {days} दिनों के लिए प्रीमियम एक्सेस है। आनंद लें! 💎"
            ),
            'payment_rejected': (
                "❌ भुगतान अस्वीकृत\n\n"
                "आपका भुगतान प्रमाण अस्वीकार कर दिया गया था। विवरण के लिए कृपया व्यवस्थापक से संपर्क करें।"
            ),
            # Button texts
            'btn_help': "❓ मदद",
            'btn_stats': "📊 मेरे आंकड़े",
            'btn_referral': "🎁 रेफरल",
            'btn_premium': "💎 प्रीमियम",
            'btn_buy_premium': "💳 प्रीमियम खरीदें",
            'btn_upgrade_premium': "⬆️ प्रीमियम में अपग्रेड करें",
            'btn_main_menu': "🏠 मुख्य मेनू",
            'btn_new_video': "🆕 नया वीडियो",
            'btn_upi_payment': "💰 UPI भुगतान (भारत)",
            'btn_stars_payment': "⭐ Telegram Stars",
            'btn_back': "⬅️ वापस",
            'btn_upload_proof': "📸 भुगतान प्रमाण अपलोड करें",
        },
    }
    
    LANGUAGE_NAMES = {
        'en': 'English 🇬🇧',
        'es': 'Español 🇪🇸',
        'hi': 'हिंदी 🇮🇳',
    }
    
    def __init__(self, default_language: str = 'en'):
        """Initialize i18n with default language."""
        self.default_language = default_language
        self.user_languages = {}
    
    def detect_language(self, text: str) -> str:
        """
        Auto-detect language from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Detected language code or default
        """
        try:
            detected = detect(text)
            # Map detected language to supported languages
            if detected in self.TRANSLATIONS:
                logger.info(f"Detected language: {detected}")
                return detected
            # Return default if not supported
            return self.default_language
        except LangDetectException:
            logger.warning(f"Could not detect language from: {text}")
            return self.default_language
    
    def set_user_language(self, user_id: int, language: str):
        """Set language preference for a user."""
        if language in self.TRANSLATIONS:
            self.user_languages[user_id] = language
            logger.info(f"Set language for user {user_id}: {language}")
        else:
            logger.warning(f"Unsupported language: {language}")
    
    def get_user_language(self, user_id: int, language_code: str = None) -> str:
        """
        Get user's preferred language.
        
        Args:
            user_id: User ID
            language_code: Optional language code from Telegram
            
        Returns:
            Language code
        """
        # Priority: user setting > stored preference > Telegram language > default
        if user_id in self.user_languages:
            return self.user_languages[user_id]
        
        if language_code and language_code in self.TRANSLATIONS:
            return language_code
        
        return self.default_language
    
    def get_text(self, key: str, user_id: int = None, language_code: str = None, 
                 **kwargs) -> str:
        """
        Get translated text for a user.
        
        Args:
            key: Translation key
            user_id: User ID for language preference
            language_code: Optional language code
            **kwargs: Format parameters
            
        Returns:
            Translated and formatted text
        """
        lang = self.get_user_language(user_id, language_code) if user_id else self.default_language
        
        translations = self.TRANSLATIONS.get(lang, self.TRANSLATIONS[self.default_language])
        text = translations.get(key, self.TRANSLATIONS[self.default_language].get(key, key))
        
        # Format with provided kwargs
        try:
            return text.format(**kwargs)
        except KeyError as e:
            logger.error(f"Missing format parameter for key '{key}': {e}")
            return text
    
    def get_available_languages(self) -> Dict[str, str]:
        """Get list of available languages."""
        return self.LANGUAGE_NAMES.copy()
