/** Contenu statique du mode observateur (vitrine publique). */

export const publicNavLinks = [
  { to: '/accueil', label: 'Accueil', exact: true },
  { to: '/a-propos', label: 'À propos' },
  { to: '/presentation', label: 'Présentation' },
  { to: '/nos-services', label: 'Services' },
  { to: '/securite', label: 'Sécurité' },
  { to: '/faq', label: 'FAQ' },
  { to: '/temoignages', label: 'Témoignages' },
  { to: '/blog', label: 'Conseils santé' },
  { to: '/contact', label: 'Contact' },
]

export const highlightCards = [
  {
    title: 'Infrastructure moderne',
    text: 'Locaux équipés pour des soins confortables et efficaces.',
    icon: 'building',
    image: '/images/visitor/infra.jpg',
  },
  {
    title: 'Équipe médicale',
    text: 'Médecins, infirmiers et secrétariat à votre écoute.',
    icon: 'team',
    image: '/images/visitor/equipe.jpg',
  },
  {
    title: 'Laboratoire certifié',
    text: 'Analyses fiables avec résultats consultables en ligne.',
    icon: 'lab',
    image: '/images/visitor/labo.jpg',
  },
]

export const serviceCards = [
  {
    id: 'consultations',
    title: 'Consultations & RDV',
    text: 'Planifiez une consultation présentielle ou en téléconsultation.',
    icon: 'heart',
    redirect: '/patient/rendez-vous',
    cta: 'Prendre rendez-vous',
  },
  {
    id: 'pharmacie',
    title: 'Pharmacie',
    text: 'Ordonnances validées et suivi de vos traitements.',
    icon: 'pharmacy',
    redirect: '/patient/prescriptions',
    cta: 'Voir mes ordonnances',
  },
  {
    id: 'analyses',
    title: 'Laboratoire',
    text: 'Résultats d’analyses téléchargeables en PDF.',
    icon: 'lab',
    redirect: '/patient/laboratoire',
    cta: 'Voir mes analyses',
  },
  {
    id: 'soins',
    title: 'Soins',
    text: 'Constantes, plans de soins et suivi infirmier.',
    icon: 'care',
    redirect: '/patient/soins',
    cta: 'Accéder aux soins',
  },
  {
    id: 'factures',
    title: 'Factures',
    text: 'Consultez et réglez vos factures en toute sécurité.',
    icon: 'billing',
    redirect: '/patient/factures',
    cta: 'Voir mes factures',
  },
  {
    id: 'urgence',
    title: 'Service 24/7',
    text: 'Accès à votre espace patient à tout moment.',
    icon: 'clock',
    redirect: '/patient',
    cta: 'Ouvrir mon espace',
  },
]

export const trustFeatures = [
  { title: 'Accès 24/7', text: 'Votre portail est disponible jour et nuit.', icon: 'clock' },
  { title: 'PDF résultats', text: 'Documents médicaux téléchargeables.', icon: 'pdf' },
  { title: 'Paiement mobile', text: 'MTN, Orange Money et carte bancaire.', icon: 'mobile' },
]

export const securityPoints = [
  {
    title: '100 % chiffré',
    text: 'Connexion sécurisée (HTTPS) et tokens JWT avec rotation.',
  },
  {
    title: 'Conformité RGPD',
    text: 'Consentement explicite, droit d’accès et données minimisées.',
  },
  {
    title: 'Paiement sécurisé',
    text: 'Transactions protégées — aucun numéro de carte stocké en clair.',
  },
  {
    title: 'Contrôle des accès',
    text: 'Chaque rôle (patient, médecin, secrétaire…) voit uniquement son espace.',
  },
]

export const faqItems = [
  {
    q: 'Puis-je consulter le site sans compte ?',
    a: 'Oui. Le mode observateur vous laisse découvrir l’établissement, les services, la FAQ et les conseils santé. Pour vos données personnelles (RDV, factures, dossier), une connexion est nécessaire.',
  },
  {
    q: 'Comment prendre un rendez-vous ?',
    a: 'Créez un compte patient (gratuit), connectez-vous, puis envoyez une demande. Elle apparaît « en attente » jusqu’à validation par le secrétariat.',
  },
  {
    q: 'Comment obtenir mes résultats d’analyses ?',
    a: 'Une fois connecté, ouvrez « Laboratoire ». Les résultats publiés sont consultables et téléchargeables en PDF.',
  },
  {
    q: 'Quels moyens de paiement sont acceptés ?',
    a: 'Paiement mobile (MTN, Orange Money) et carte bancaire via le portail patient, de façon sécurisée.',
  },
  {
    q: 'Mes données de santé sont-elles protégées ?',
    a: 'Oui. Les échanges sont chiffrés, l’accès est contrôlé par rôle, et le traitement respecte le RGPD.',
  },
  {
    q: 'Le personnel peut-il s’inscrire seul ?',
    a: 'Non. Les comptes staff (médecin, secrétaire, etc.) sont créés par l’administration. Seuls les patients s’inscrivent en ligne.',
  },
]

export const testimonials = [
  {
    id: 1,
    initials: 'A.M.',
    role: 'Patiente',
    quote: 'J’ai pu demander un rendez-vous en quelques minutes. Le suivi et les messages du secrétariat m’ont rassurée.',
  },
  {
    id: 2,
    initials: 'J.K.',
    role: 'Patient',
    quote: 'Consulter mes résultats et factures depuis mon téléphone, c’est un vrai gain de temps.',
  },
  {
    id: 3,
    initials: 'S.L.',
    role: 'Patiente',
    quote: 'L’interface est claire et bienveillante. Je me sens accompagnée, même à distance.',
  },
  {
    id: 4,
    initials: 'Dr. P.',
    role: 'Médecin partenaire',
    quote: 'Grâce à SGHL, la coordination des rendez-vous avec le secrétariat est beaucoup plus fluide.',
  },
]

export const blogPosts = [
  {
    slug: 'bien-s-hydrater',
    title: 'Bien s’hydrater au quotidien',
    excerpt: 'Pourquoi l’eau reste le premier geste santé, surtout sous un climat chaud.',
    tag: 'Prévention',
    readMinutes: 3,
    image: '/images/visitor/blog-hydratation.jpg',
    body: [
      'Boire régulièrement aide le corps à réguler la température, digérer et éliminer les toxines.',
      'Visez environ 1,5 à 2 litres d’eau par jour, davantage en cas de chaleur ou d’activité physique.',
      'Préférez l’eau aux boissons sucrées. Les fruits riches en eau (pastèque, orange) complètent utilement votre apport.',
    ],
  },
  {
    slug: 'prevention-nutrition',
    title: 'Prévention et nutrition',
    excerpt: 'Des repères simples pour une assiette équilibrée sans régime extrême.',
    tag: 'Nutrition',
    readMinutes: 4,
    image: '/images/visitor/blog-nutrition.jpg',
    body: [
      'Alternez légumes, protéines (poissons, légumineuses, viandes maigres) et féculents complets.',
      'Réduisez le sel et les fritures : privilégiez la vapeur, le grill ou le four.',
      'Un petit-déjeuner régulier et des repas à heures stables aident aussi le suivi médical (glycémie, tension…).',
    ],
  },
  {
    slug: 'prevention-paludisme',
    title: 'Prévention du paludisme',
    excerpt: 'Gestes essentiels pour se protéger et quand consulter.',
    tag: 'Urgences',
    readMinutes: 4,
    image: '/images/visitor/blog-paludisme.jpg',
    body: [
      'Utilisez des moustiquaires imprégnées et des répulsifs adaptés, surtout le soir.',
      'Évitez les eaux stagnantes près du domicile qui favorisent les moustiques.',
      'Fièvre, frissons, maux de tête : consultez rapidement. Un diagnostic et un traitement précoces changent tout.',
    ],
  },
  {
    slug: 'gestion-du-stress',
    title: 'Gérer le stress au quotidien',
    excerpt: 'Techniques courtes pour calmer le corps et l’esprit.',
    tag: 'Bien-être',
    readMinutes: 3,
    image: '/images/visitor/equipe.jpg',
    body: [
      'La respiration lente (inspirer 4 secondes, expirer 6) active le système nerveux parasympathique.',
      'Une marche de 15 minutes ou un temps sans écran avant le coucher améliore souvent le sommeil.',
      'Si l’anxiété gêne votre vie quotidienne, parlez-en à un professionnel de santé via votre espace SGHL.',
    ],
  },
  {
    slug: 'prevention-diabete',
    title: 'Prévention du diabète',
    excerpt: 'Alimentation, activité et dépistage : les bases utiles.',
    tag: 'Prévention',
    readMinutes: 4,
    image: '/images/visitor/blog-nutrition.jpg',
    body: [
      'Surveillez le sucre ajouté et les boissons industrielles.',
      '30 minutes d’activité modérée la plupart des jours de la semaine réduisent le risque.',
      'Un bilan périodique (glycémie) permet de détecter un prédiabète à temps — demandez conseil à votre médecin.',
    ],
  },
]

export function getBlogPost(slug) {
  return blogPosts.find((p) => p.slug === slug) || null
}
