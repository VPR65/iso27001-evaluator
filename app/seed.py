from sqlmodel import Session, select
from app.models import ControlDefinition, User, Client, UserRole, Norma
from app.database import engine
from app.auth import hash_password

NORMAS = [
    {
        "code": "ISO27001",
        "name": "ISO/IEC 27001:2022",
        "version": "2022",
        "description": "Sistema de Gestion de Seguridad de la Informacion",
    },
    {
        "code": "ISO9001",
        "name": "ISO 9001:2015",
        "version": "2015",
        "description": "Sistema de Gestion de la Calidad",
    },
    {
        "code": "ISO20000",
        "name": "ISO/IEC 20000-1:2018",
        "version": "2018",
        "description": "Sistema de Gestion de Servicios de TI",
    },
    {
        "code": "ISO22301",
        "name": "ISO 22301:2019",
        "version": "2019",
        "description": "Sistema de Gestion de Continuidad del Negocio",
    },
    {
        "code": "ITIL4",
        "name": "ITIL v4 Framework",
        "version": "4.0",
        "description": "Framework de Gestion de Servicios de TI",
    },
]


def _get_itil4_controls():
    return [
        {
            "code": "ITSV-1",
            "domain": "SVS - Service Value System",
            "title": "Service Value System",
            "description": "El SVS determina como los recursos se transforman en valor a traves de actividades y gobernanza.",
        },
        {
            "code": "ITSV-2",
            "domain": "4 Dimensions Model",
            "title": "Four Dimensions of Service Value",
            "description": "Las cuatro dimensiones que deben estar balanceadas para la creacion de valor.",
        },
        {
            "code": "GOV-1",
            "domain": "Governance - Direct",
            "title": "Direct and Justify",
            "description": "Direccionar y justificar las politicas, regulaciones y estrategas de la organizacion.",
        },
        {
            "code": "GOV-2",
            "domain": "Governance - Plan",
            "title": "Plan and Set Direction",
            "description": "Planificar y establecer la direccion estrategica y tactica de la organizacion.",
        },
        {
            "code": "GOV-3",
            "domain": "Governance - Improve",
            "title": "Improve and Achieve Objectives",
            "description": "Mejorar continuamente y lograr los objetivos de la organizacion.",
        },
        {
            "code": "VST-1",
            "domain": "Value Streams and Pathways",
            "title": "Design and Engineer",
            "description": "Disenar e ingenierar servicios para crear valor.",
        },
        {
            "code": "VST-2",
            "domain": "Value Streams and Pathways",
            "title": "Deliver and Support",
            "description": "Entregar y soportar servicios para generar valor.",
        },
        {
            "code": "OPE-1",
            "domain": "Operating Model",
            "title": "Change Enablement",
            "description": "Maximizar la probabilidad de resultados exitosos de cambios.",
        },
        {
            "code": "OPE-2",
            "domain": "Operating Model",
            "title": "Incident Management",
            "description": "Minimizar el impacto negativo de incidentes restaurando el servicio normal.",
        },
        {
            "code": "OPE-3",
            "domain": "Operating Model",
            "title": "Problem Management",
            "description": "Reducir la probabilidad e impacto de incidentes eliminando errores.",
        },
        {
            "code": "OPE-4",
            "domain": "Operating Model",
            "title": "Service Request Management",
            "description": "Soportar la carga de trabajo predefinida y auto-servicio.",
        },
        {
            "code": "OPE-5",
            "domain": "Operating Model",
            "title": "IT Asset Management",
            "description": "Planificar y gestionar el ciclo de vida de los activos de TI.",
        },
        {
            "code": "IMP-1",
            "domain": "Improvement - Continual",
            "title": "Continual Improvement",
            "description": "Alinear las practicas de mejora con las necesidades actuales y futuras.",
        },
        {
            "code": "IMP-2",
            "domain": "Improvement - Measurement",
            "title": "Measurement and Reporting",
            "description": "Definir y capturar metricas para demostrar valor y mejora.",
        },
        {
            "code": "REL-1",
            "domain": "Relationships",
            "title": "Business Analysis",
            "description": "Identificar necesidades y oportunidades de negocio.",
        },
        {
            "code": "REL-2",
            "domain": "Relationships",
            "title": "Portfolio Management",
            "description": "Gestionar portafolio de servicios, productos y recursos.",
        },
        {
            "code": "REL-3",
            "domain": "Relationships",
            "title": "Relationship Management",
            "description": "Fomentar relaciones positivas y trabajar con stakeholders.",
        },
        {
            "code": "SUP-1",
            "domain": "Supply and Demand",
            "title": "Supplier Management",
            "description": "Asegurar que los proveedores entreguen valor sostenible.",
        },
        {
            "code": "SUP-2",
            "domain": "Supply and Demand",
            "title": "Service Level Management",
            "description": "Establecer y mantener acuerdos de nivel de servicio.",
        },
        {
            "code": "SUP-3",
            "domain": "Supply and Demand",
            "title": "Service Configuration",
            "description": "Asegurar informacion akuratica de configuracion de servicios.",
        },
        {
            "code": "TEC-1",
            "domain": "Technical Practices",
            "title": "Deployment Management",
            "description": "Mover servicios nuevos o modificados a produccion.",
        },
        {
            "code": "TEC-2",
            "domain": "Technical Practices",
            "title": "Infrastructure and Platform",
            "description": "Gestionar infraestructura y plataformas de servicios.",
        },
        {
            "code": "TEC-3",
            "domain": "Technical Practices",
            "title": "Software Development",
            "description": "Desarrollar y mantener software de servicios.",
        },
        {
            "code": "TEC-4",
            "domain": "Technical Practices",
            "title": "Security Management",
            "description": "Proteger la informacion y los datos de la organizacion.",
        },
        {
            "code": "SVC-1",
            "domain": "Service Value Chain",
            "title": "Engage and Plan",
            "description": "Proveer vision clara, retroalimentacion y mejora continua.",
        },
        {
            "code": "SVC-2",
            "domain": "Service Value Chain",
            "title": "Design and Transition",
            "description": "Disenar y desarrollar nuevos servicios y caracteristicas.",
        },
        {
            "code": "SVC-3",
            "domain": "Service Value Chain",
            "title": "Obtain and Build",
            "description": "Asegurar que componentes de servicio esten disponibles.",
        },
        {
            "code": "SVC-4",
            "domain": "Service Value Chain",
            "title": "Deliver and Support",
            "description": "Entregar servicios de acuerdo a especificaciones.",
        },
        {
            "code": "ADD-1",
            "domain": "Organization and People",
            "title": "Organizational Change Management",
            "description": "Preparar a personas para cambios organizacionales.",
        },
        {
            "code": "ADD-2",
            "domain": "Organization and People",
            "title": "Workforce and Talent Management",
            "description": "Desarrollar capacidades y competencias del personal.",
        },
        {
            "code": "ADD-3",
            "domain": "Information and Technology",
            "title": "Information Security Management",
            "description": "Proteger la informacion mediante controles de seguridad.",
        },
        {
            "code": "ADD-4",
            "domain": "Information and Technology",
            "title": "Knowledge Management",
            "description": "Mantener y mejorar el conocimiento organizacional.",
        },
        {
            "code": "ADD-5",
            "domain": "Partners and Suppliers",
            "title": "Vendor Assessment",
            "description": "Evaluar capacidades y riesgos de proveedores.",
        },
    ]


ISO_CONTROLS = [
    # A.5 Controles Organizacionales (37)
    {
        "code": "A.5.1",
        "domain": "Controles Organizacionales (A.5)",
        "title": "Politicas de seguridad de la informacion",
        "description": "Se debe establecer, aprobar, publicar y comunicar un conjunto de politicas de seguridad de la informacion alineado con los objetivos del negocio.",
    },
    {
        "code": "A.5.2",
        "domain": "Controles Organizacionales (A.5)",
        "title": "Roles y responsabilidades de seguridad",
        "description": "Deben definirse, documentarse y asignarse claramente todos los roles y responsabilidades de seguridad de la informacion.",
    },
    {
        "code": "A.5.3",
        "domain": "Controles Organizacionales (A.5)",
        "title": "Separacion de funciones",
        "description": "Deben separarse las funciones conflictivas para reducir oportunidades de modificacion no autorizada o uso indebido.",
    },
    {
        "code": "A.5.4",
        "domain": "Controles Organizacionales (A.5)",
        "title": "Responsabilidades de la direccion",
        "description": "La direccion debe definir, aprobar, asignar y documentar las responsabilidades de seguridad de la informacion.",
    },
    {
        "code": "A.5.5",
        "domain": "Controles Organizacionales (A.5)",
        "title": "Contacto con autoridades",
        "description": "Deben mantenerse contactos apropiados con autoridades relevantes de seguridad y cumplimiento.",
    },
    {
        "code": "A.5.6",
        "domain": "Controles Organizacionales (A.5)",
        "title": "Contacto con grupos de interes especial",
        "description": "Deben mantenerse contactos apropiados con grupos de interes especial en seguridad y otros foros especializados.",
    },
    {
        "code": "A.5.7",
        "domain": "Controles Organizacionales (A.5)",
        "title": "Inteligencia de amenazas",
        "description": "Debe recopilare y analizarse informacion sobre amenazas a la seguridad de la informacion para identificar y gestionar riesgos de manera proactiva.",
    },
    {
        "code": "A.5.8",
        "domain": "Controles Organizacionales (A.5)",
        "title": "Seguridad en la gestion de proyectos",
        "description": "La seguridad de la informacion debe abordarse en la gestion de proyectos independientemente del tipo de proyecto.",
    },
    {
        "code": "A.5.9",
        "domain": "Controles Organizacionales (A.5)",
        "title": "Inventario de activos de informacion",
        "description": "Debe elaborarse y mantenerse un inventario de activos de informacion y otros activos asociados.",
    },
    {
        "code": "A.5.10",
        "domain": "Controles Organizacionales (A.5)",
        "title": "Uso aceptable de activos de informacion",
        "description": "Deben definirse y documentarse reglas para el uso aceptable de activos de informacion y activos asociados.",
    },
    {
        "code": "A.5.11",
        "domain": "Controles Organizacionales (A.5)",
        "title": "Devolucion de activos",
        "description": "Deben definirse e implementarse procedimientos para la entrega y devolucion formal de activos.",
    },
    {
        "code": "A.5.12",
        "domain": "Controles Organizacionales (A.5)",
        "title": "Clasificacion de la informacion",
        "description": "La informacion debe clasificarse en funcion de los requisitos legales, valor, criticidad y susceptibilidad a revelarse.",
    },
    {
        "code": "A.5.13",
        "domain": "Controles Organizacionales (A.5)",
        "title": "Etiquetado de la informacion",
        "description": "Debe elaborarse e implementarse un conjunto de procedimientos de etiquetado para la informacion de acuerdo con la clasificacion adoptada.",
    },
    {
        "code": "A.5.14",
        "domain": "Controles Organizacionales (A.5)",
        "title": "Transferencia de informacion",
        "description": "Debe existir una politica y controles para asegurar la transferencia de informacion dentro y fuera de la organizacion.",
    },
    {
        "code": "A.5.15",
        "domain": "Controles Organizacionales (A.5)",
        "title": "Control de acceso",
        "description": "Debe establecerse una politica de control de acceso basada en requisitos del negocio y de seguridad de la informacion.",
    },
    {
        "code": "A.5.16",
        "domain": "Controles Organizacionales (A.5)",
        "title": "Gestion de identidades",
        "description": "Debe gestionarse el ciclo de vida de las identidades de usuarios, incluyendo su creacion, modificacion y eliminacion.",
    },
    {
        "code": "A.5.17",
        "domain": "Controles Organizacionales (A.5)",
        "title": "Informacion de autenticacion",
        "description": "Deben gestionarse los derechos de acceso y la informacion de autenticacion de manera segura.",
    },
    {
        "code": "A.5.18",
        "domain": "Controles Organizacionales (A.5)",
        "title": "Derechos de acceso",
        "description": "Deben definirse y gestionarse los derechos de acceso de los usuarios de acuerdo con la politica de control de acceso.",
    },
    {
        "code": "A.5.19",
        "domain": "Controles Organizacionales (A.5)",
        "title": "Seguridad en acuerdos con terceros",
        "description": "Deben acordarse e implementarse requisitos de seguridad de la informacion con cada proveedor.",
    },
    {
        "code": "A.5.20",
        "domain": "Controles Organizacionales (A.5)",
        "title": "Gestion de riesgos en proveedores",
        "description": "Deben gestionarse los riesgos asociados con el acceso de proveedores a los activos de la organizacion.",
    },
    {
        "code": "A.5.21",
        "domain": "Controles Organizacionales (A.5)",
        "title": "Seguridad de la cadena de suministro ICT",
        "description": "Deben identificarse e implementarse controles para gestionar los riesgos de seguridad de la cadena de suministro ICT.",
    },
    {
        "code": "A.5.22",
        "domain": "Controles Organizacionales (A.5)",
        "title": "Monitoreo de proveedores",
        "description": "Deben monitorearse y revisarse periodicamente las actividades de los proveedores.",
    },
    {
        "code": "A.5.23",
        "domain": "Controles Organizacionales (A.5)",
        "title": "Gestion de cambios en servicios de proveedores",
        "description": "Los cambios en los servicios de los proveedores deben gestionarse, incluyendo revision y actualizacion de acuerdos.",
    },
    {
        "code": "A.5.24",
        "domain": "Controles Organizacionales (A.5)",
        "title": "Gestion de incidentes de seguridad",
        "description": "Deben establecerse procesos de gestion de incidentes de seguridad con responsabilidades y procedimientos claros.",
    },
    {
        "code": "A.5.25",
        "domain": "Controles Organizacionales (A.5)",
        "title": "Evaluacion y decision sobre incidentes",
        "description": "Los incidentes deben evaluarse para determinar si son incidentes de seguridad de la informacion y clasificarse apropiadamente.",
    },
    {
        "code": "A.5.26",
        "domain": "Controles Organizacionales (A.5)",
        "title": "Respuesta a incidentes de seguridad",
        "description": "Deben definirse e implementarse procedimientos de respuesta a incidentes de seguridad de la informacion.",
    },
    {
        "code": "A.5.27",
        "domain": "Controles Organizacionales (A.5)",
        "title": "Lecciones aprendidas de incidentes",
        "description": "Debe analizarse la informacion sobre incidentes para extraer lecciones aprendidas y mejorar controles.",
    },
    {
        "code": "A.5.28",
        "domain": "Controles Organizacionales (A.5)",
        "title": "Recoleccion de evidencia",
        "description": "Deben definirse y aplicarse procedimientos para la recoleccion y preservacion de evidencia relacionada con incidentes.",
    },
    {
        "code": "A.5.29",
        "domain": "Controles Organizacionales (A.5)",
        "title": "Continuidad de seguridad de la informacion",
        "description": "La seguridad de la informacion debe integrarse en los sistemas de gestion de continuidad del negocio.",
    },
    {
        "code": "A.5.30",
        "domain": "Controles Organizacionales (A.5)",
        "title": "Redundancia de instalaciones de procesamiento",
        "description": "Deben implementarse recursos de procesamiento de informacion con redundancia apropiada para garantizar disponibilidad.",
    },
    {
        "code": "A.5.31",
        "domain": "Controles Organizacionales (A.5)",
        "title": "Identificacion de requisitos legales y contractuales",
        "description": "Deben identificarse y revisarse los requisitos legales, regulatorios y contractuales aplicables a la seguridad de la informacion.",
    },
    {
        "code": "A.5.32",
        "domain": "Controles Organizacionales (A.5)",
        "title": "Derechos de propiedad intelectual",
        "description": "Deben protegerse los derechos de propiedad intelectual de la organizacion mediante el cumplimiento de leyes y regulaciones.",
    },
    {
        "code": "A.5.33",
        "domain": "Controles Organizacionales (A.5)",
        "title": "Proteccion de registros",
        "description": "Los registros deben protegerse contra modificacion, eliminacion, dano y acceso no autorizado.",
    },
    {
        "code": "A.5.34",
        "domain": "Controles Organizacionales (A.5)",
        "title": "Privacidad y proteccion de PII",
        "description": "Debe garantizarse la privacidad y proteccion de la informacion personal de acuerdo con las leyes de proteccion de datos aplicables.",
    },
    {
        "code": "A.5.35",
        "domain": "Controles Organizacionales (A.5)",
        "title": "Revision independiente de la seguridad",
        "description": "Las politicas y procedimientos de seguridad deben revisarse de forma independiente a intervalos planificados.",
    },
    {
        "code": "A.5.36",
        "domain": "Controles Organizacionales (A.5)",
        "title": "Cumplimiento con politicas y reglas de seguridad",
        "description": "Los directivos deben revisar periodicamente el cumplimiento de los empleados con las politicas y procedimientos de seguridad.",
    },
    {
        "code": "A.5.37",
        "domain": "Controles Organizacionales (A.5)",
        "title": "Procedimientos operativos documentados",
        "description": "Los procedimientos operacionales deben documentarse, mantenerse y estar disponibles para todos los usuarios que los necesiten.",
    },
    # A.6 Controles de Personas (8)
    {
        "code": "A.6.1",
        "domain": "Controles de Personas (A.6)",
        "title": "Verificacion de antecedentes",
        "description": "Deben verificarse los antecedentes de candidatos a puestos de trabajo, en la medida permitida por las leyes y etica, antes de incorporarse.",
    },
    {
        "code": "A.6.2",
        "domain": "Controles de Personas (A.6)",
        "title": "Terminos y condiciones de empleo",
        "description": "Los acuerdos laborales deben establecer las responsabilidades de seguridad de la informacion del empleado, contratista y terceros.",
    },
    {
        "code": "A.6.3",
        "domain": "Controles de Personas (A.6)",
        "title": "Concienciacion, educacion y formacion en seguridad",
        "description": "Debe proporcionarse formacion de concienciacion y educacion en seguridad de la informacion a todos los empleados y partes interesadas.",
    },
    {
        "code": "A.6.4",
        "domain": "Controles de Personas (A.6)",
        "title": "Proceso disciplinario",
        "description": "Debe existir un proceso disciplinario formal para abordar incidentes de seguridad de la informacion.",
    },
    {
        "code": "A.6.5",
        "domain": "Controles de Personas (A.6)",
        "title": "Responsabilidades tras la finalizacion",
        "description": "Las responsabilidades de seguridad de la informacion deben mantenerse despues del cambio de puesto o finalizacion del empleo.",
    },
    {
        "code": "A.6.6",
        "domain": "Controles de Personas (A.6)",
        "title": "Acuerdos de confidencialidad y no divulgacion",
        "description": "Deben identificarse y revisarse los acuerdos de confidencialidad y no divulgacion que reflejen las necesidades de la organizacion.",
    },
    {
        "code": "A.6.7",
        "domain": "Controles de Personas (A.6)",
        "title": "Teletrabajo",
        "description": "Debe adoptarse una politica y controles de seguridad para gestionar los riesgos derivados del teletrabajo.",
    },
    {
        "code": "A.6.8",
        "domain": "Controles de Personas (A.6)",
        "title": "Reporte de eventos de seguridad",
        "description": "Los empleados y partes interesadas deben reportar los eventos de seguridad de la informacion a traves de canales apropiados.",
    },
    # A.7 Controles Fisicos (14)
    {
        "code": "A.7.1",
        "domain": "Controles Físicos (A.7)",
        "title": "Perimetros de seguridad fisica",
        "description": "Deben definirse y usarse perimetros de seguridad fisica para proteger areas que contengan informacion sensible o critica.",
    },
    {
        "code": "A.7.2",
        "domain": "Controles Físicos (A.7)",
        "title": "Controles de acceso fisico",
        "description": "Deben implementarse controles de acceso fisico para proteger contra amenazas al perimetro de seguridad.",
    },
    {
        "code": "A.7.3",
        "domain": "Controles Físicos (A.7)",
        "title": "Seguridad de oficinas, salas y facilities",
        "description": "Deben disenarse y aplicarse seguridad fisica para oficinas, salas y facilities.",
    },
    {
        "code": "A.7.4",
        "domain": "Controles Físicos (A.7)",
        "title": "Monitoreo de seguridad fisica",
        "description": "Debe implementarse monitoreo de seguridad fisica para las instalaciones, incluyendo CCTV y sistemas de deteccion.",
    },
    {
        "code": "A.7.5",
        "domain": "Controles Físicos (A.7)",
        "title": "Proteccion contra amenazas fisicas y ambientales",
        "description": "Debe disenarse e implementarse proteccion fisica contra incendios, inundaciones, terremotos y otros desastres naturales.",
    },
    {
        "code": "A.7.6",
        "domain": "Controles Físicos (A.7)",
        "title": "Trabajo en areas seguras",
        "description": "Deben implementarse controles de seguridad fisica para proteger el personal que trabaja en areas seguras.",
    },
    {
        "code": "A.7.7",
        "domain": "Controles Físicos (A.7)",
        "title": "Entrega y devolucion limpia de escritorio",
        "description": "Deben aplicarse politicas de escritorio limpio y pantalla limpia para reducir el riesgo de acceso no autorizado a informacion.",
    },
    {
        "code": "A.7.8",
        "domain": "Controles Físicos (A.7)",
        "title": "Politica de equipo desatendido",
        "description": "Los usuarios deben asegurar que equipos desatendidos tengan la proteccion adecuada, incluyendo bloqueo de pantalla.",
    },
    {
        "code": "A.7.9",
        "domain": "Controles Físicos (A.7)",
        "title": "Politica de uso de dispositivos moviles",
        "description": "Debe adoptarse una politica y controles de seguridad para gestionar los riesgos derivados del uso de dispositivos moviles.",
    },
    {
        "code": "A.7.10",
        "domain": "Controles Físicos (A.7)",
        "title": "Medios de almacenamiento",
        "description": "Deben gestionarse de forma segura los medios de almacenamiento que contengan informacion, incluyendo su transporte y disposicion.",
    },
    {
        "code": "A.7.11",
        "domain": "Controles Físicos (A.7)",
        "title": "Servicios de apoyo",
        "description": "Deben protegerse los servicios de apoyo como electricidad, telecomunicaciones y agua que dependan los sistemas de informacion.",
    },
    {
        "code": "A.7.12",
        "domain": "Controles Físicos (A.7)",
        "title": "Seguridad del cableado",
        "description": "Los cables de datos, de alimentacion electrica y de telecomunicaciones deben protegerse contra interceptacion o dano.",
    },
    {
        "code": "A.7.13",
        "domain": "Controles Físicos (A.7)",
        "title": "Mantenimiento de equipos",
        "description": "El mantenimiento de equipos debe realizarse segun las instrucciones y requisitos de seguridad documentados.",
    },
    {
        "code": "A.7.14",
        "domain": "Controles Físicos (A.7)",
        "title": "Eliminacion o reutilizacion segura de equipos",
        "description": "Debe verificarse que los equipos que contengan informacion sean eliminados o reutilizados de forma segura.",
    },
    # A.8 Controles Tecnologicos (34)
    {
        "code": "A.8.1",
        "domain": "Controles Tecnológicos (A.8)",
        "title": "Dispositivos de punto final del usuario",
        "description": "Deben implementarse politicas y procedimientos de gestion de dispositivos de punto final para proteger la informacion.",
    },
    {
        "code": "A.8.2",
        "domain": "Controles Tecnológicos (A.8)",
        "title": "Derechos de acceso privilegiado",
        "description": "Deben restringirse los derechos de acceso privilegiado a sistemas y aplicaciones de acuerdo con las necesidades del negocio.",
    },
    {
        "code": "A.8.3",
        "domain": "Controles Tecnológicos (A.8)",
        "title": "Restriccion de acceso a la informacion",
        "description": "Deben implementarse restricciones de acceso a la informacion y funciones de los sistemas de aplicacion.",
    },
    {
        "code": "A.8.4",
        "domain": "Controles Tecnológicos (A.8)",
        "title": "Acceso al codigo fuente",
        "description": "Debe controlarse el acceso al codigo fuente de las aplicaciones para prevenir modificaciones no autorizadas.",
    },
    {
        "code": "A.8.5",
        "domain": "Controles Tecnológicos (A.8)",
        "title": "Autenticacion segura",
        "description": "Deben implementarse mecanismos de autenticacion seguros para validar la identidad de los usuarios.",
    },
    {
        "code": "A.8.6",
        "domain": "Controles Tecnológicos (A.8)",
        "title": "Gestion de capacidades",
        "description": "Debe monitorearse y ajustarse el uso de recursos de sistemas, proyectarse capacidades futuras y aplicarse remediacion.",
    },
    {
        "code": "A.8.7",
        "domain": "Controles Tecnológicos (A.8)",
        "title": "Proteccion contra software malicioso",
        "description": "Deben implementarse controles de deteccion, prevencion y recuperacion contra malware.",
    },
    {
        "code": "A.8.8",
        "domain": "Controles Tecnológicos (A.8)",
        "title": "Gestion de vulnerabilidades tecnicas",
        "description": "Debe evaluarse y tratarse apropiadamente las vulnerabilidades tecnicas en la informacion y los sistemas.",
    },
    {
        "code": "A.8.9",
        "domain": "Controles Tecnológicos (A.8)",
        "title": "Gestion de configuraciones",
        "description": "Deben establecerse, documentarse, implementarse y monitorearse configuraciones de seguridad de los sistemas.",
    },
    {
        "code": "A.8.10",
        "domain": "Controles Tecnológicos (A.8)",
        "title": "Eliminacion de informacion",
        "description": "Debe verificarse que la informacion sea eliminada de forma segura cuando ya no se requiera, usando metodos apropiados.",
    },
    {
        "code": "A.8.11",
        "domain": "Controles Tecnológicos (A.8)",
        "title": "Enmascaramiento de datos",
        "description": "Deben implementarse controles de enmascaramiento de datos para proteger la informacion sensible segun las politicas de la organizacion.",
    },
    {
        "code": "A.8.12",
        "domain": "Controles Tecnológicos (A.8)",
        "title": "Prevencion de fuga de datos (DLP)",
        "description": "Deben implementarse controles DLP para detectar y prevenir la fuga de informacion sensible.",
    },
    {
        "code": "A.8.13",
        "domain": "Controles Tecnológicos (A.8)",
        "title": "Respaldo de informacion",
        "description": "Deben realizarse copias de seguridad de informacion, software y sistemas de acuerdo con la politica de backup.",
    },
    {
        "code": "A.8.14",
        "domain": "Controles Tecnológicos (A.8)",
        "title": "Redundancia de sistemas de procesamiento de informacion",
        "description": "Deben implementarse sistemas de procesamiento de informacion con redundancia apropiada para garantizar disponibilidad.",
    },
    {
        "code": "A.8.15",
        "domain": "Controles Tecnológicos (A.8)",
        "title": "Registro (logging)",
        "description": "Deben generarse, almacenarse y protegerse registros de actividades de los sistemas para respaldar la auditoria e investigacion.",
    },
    {
        "code": "A.8.16",
        "domain": "Controles Tecnológicos (A.8)",
        "title": "Monitoreo de actividades",
        "description": "Debe monitorearse el uso de sistemas, aplicaciones y servicios para detectar comportamientos anomales.",
    },
    {
        "code": "A.8.17",
        "domain": "Controles Tecnológicos (A.8)",
        "title": "Sincronizacion de reloj",
        "description": "Los relojes de todos los sistemas de procesamiento de informacion deben sincronizarse con fuentes de tiempo precisas.",
    },
    {
        "code": "A.8.18",
        "domain": "Controles Tecnológicos (A.8)",
        "title": "Uso de programas utilitarios privilegiados",
        "description": "Debe restringirse y controlarse el uso de programas utilitarios privilegiados que puedan evadir controles de seguridad.",
    },
    {
        "code": "A.8.19",
        "domain": "Controles Tecnológicos (A.8)",
        "title": "Instalacion de software en sistemas operativos",
        "description": "Deben implementarse procedimientos para controlar la instalacion de software en sistemas operativos.",
    },
    {
        "code": "A.8.20",
        "domain": "Controles Tecnológicos (A.8)",
        "title": "Seguridad de redes",
        "description": "Las redes deben gestionarse y controlarse para proteger la informacion en sistemas y aplicaciones conectados.",
    },
    {
        "code": "A.8.21",
        "domain": "Controles Tecnológicos (A.8)",
        "title": "Seguridad de los servicios de red",
        "description": "Los mecanismos y niveles de seguridad de los servicios de red deben identificarse, implementarse y supervisarse.",
    },
    {
        "code": "A.8.22",
        "domain": "Controles Tecnológicos (A.8)",
        "title": "Segmentacion de redes",
        "description": "Las redes deben segmentarse para proteger la informacion y los sistemas de diferentes niveles de confianza.",
    },
    {
        "code": "A.8.23",
        "domain": "Controles Tecnológicos (A.8)",
        "title": "Filtrado web",
        "description": "Debe implementarse control de acceso a contenido web para limitar la exposicion a sitios web maliciosos o no autorizados.",
    },
    {
        "code": "A.8.24",
        "domain": "Controles Tecnológicos (A.8)",
        "title": "Uso de redes seguras",
        "description": "Deben implementarse controles para garantizar la seguridad de la informacion durante su transmision por redes.",
    },
    {
        "code": "A.8.25",
        "domain": "Controles Tecnológicos (A.8)",
        "title": "Desarrollo seguro",
        "description": "Los principios de ingenieria de seguridad deben establecerse, documentarse, mantenerse y aplicarse a cualquier desarrollo de sistemas.",
    },
    {
        "code": "A.8.26",
        "domain": "Controles Tecnológicos (A.8)",
        "title": "Seguridad de aplicaciones web",
        "description": "Deben implementarse controles de seguridad para proteger las aplicaciones web contra ataques comunes como inyeccion y XSS.",
    },
    {
        "code": "A.8.27",
        "domain": "Controles Tecnológicos (A.8)",
        "title": "Arquitectura segura de sistemas e ingenieria",
        "description": "Deben establecerse principios de arquitectura segura de sistemas e ingenieria de seguridad.",
    },
    {
        "code": "A.8.28",
        "domain": "Controles Tecnológicos (A.8)",
        "title": "Datos de prueba protegidos",
        "description": "Los datos de prueba deben seleccionarse cuidadosamente, protegerse y controlarse.",
    },
    {
        "code": "A.8.29",
        "domain": "Controles Tecnológicos (A.8)",
        "title": "Pruebas de seguridad en desarrollo",
        "description": "Las pruebas de funcionalidad de seguridad deben realizarse durante el desarrollo de sistemas.",
    },
    {
        "code": "A.8.30",
        "domain": "Controles Tecnológicos (A.8)",
        "title": "Desarrollo externo",
        "description": "Los acuerdos con proveedores que realicen desarrollo externo deben incluir requisitos de seguridad de la informacion.",
    },
    {
        "code": "A.8.31",
        "domain": "Controles Tecnológicos (A.8)",
        "title": "Gestion de cambios en sistemas",
        "description": "Los cambios en la organizacion, procesos de negocio, instalaciones y sistemas deben gestionarse de forma controlada.",
    },
    {
        "code": "A.8.32",
        "domain": "Controles Tecnológicos (A.8)",
        "title": "Pruebas de aceptacion",
        "description": "Deben definirse criterios de aceptacion de seguridad para nuevos sistemas, actualizaciones y nuevos desarrollos.",
    },
    {
        "code": "A.8.33",
        "domain": "Controles Tecnológicos (A.8)",
        "title": "Informacion de prueba protegida",
        "description": "La informacion de prueba de sistemas debe protegerse de la misma manera que la informacion de produccion.",
    },
    {
        "code": "A.8.34",
        "domain": "Controles Tecnológicos (A.8)",
        "title": "Controles criptograficos",
        "description": "Debe establecerse una politica sobre uso de controles criptograficos y gestionarse su ciclo de vida, incluyendo la generacion, distribucion, almacenamiento y destruccion de claves.",
    },
]


def seed_data():
    with Session(engine) as session:
        existing_norms = session.exec(select(Norma)).first()
        if existing_norms:
            print("Seed ya realizado, verificando controles faltantes...")

            # Inicializar plantillas de respuesta si no existen
            try:
                from app.routes.templates import init_templates

                superadmin = session.exec(
                    select(User).where(User.email == "admin@iso27001.local")
                ).first()
                if superadmin:
                    init_templates(session, superadmin.id)
                    print(" Plantillas de respuesta inicializadas correctamente.")
            except Exception as e:
                print(f" Error al inicializar plantillas: {e}")

            # Check and add ITIL4 controls if missing (added after initial seed)
            try:
                itil4_norma = session.exec(
                    select(Norma).where(Norma.code == "ITIL4")
                ).first()
                if itil4_norma:
                    itil_controls = session.exec(
                        select(ControlDefinition).where(
                            ControlDefinition.norma_id == itil4_norma.id
                        )
                    ).first()
                    if not itil_controls:
                        itil4_controls = _get_itil4_controls()
                        for ctrl in itil4_controls:
                            ctrl["norma_id"] = itil4_norma.id
                            session.add(ControlDefinition(**ctrl))
                        print(f"  Agregados {len(itil4_controls)} controles ITIL v4")
                        session.commit()
                        print("  Controles ITIL v4 agregados correctamente.")
            except Exception as e:
                print(f"  Error al procesar ITIL4: {e}")
                session.rollback()

            existing_superadmin = session.exec(
                select(User).where(User.email == "admin@iso27001.local")
            ).first()
            if not existing_superadmin:
                print("Creando superadmin faltante...")
                superadmin = User(
                    email="admin@iso27001.local",
                    password_hash=hash_password("admin123"),
                    name="Super Administrador",
                    role=UserRole.SUPERADMIN,
                    client_id=None,
                )
                session.add(superadmin)
                session.commit()
            return

        normas_map = {}
        for n in NORMAS:
            norma = Norma(**n)
            session.add(norma)
            session.flush()
            normas_map[n["code"]] = norma.id

        iso27001_id = normas_map["ISO27001"]

        for ctrl in ISO_CONTROLS:
            ctrl["norma_id"] = iso27001_id
            session.add(ControlDefinition(**ctrl))

        iso9001_controls = [
            {
                "code": "4.1",
                "domain": "4. Contexto de la Organizacion",
                "title": "Comprension de la organizacion y su contexto",
                "description": "La organizacion debe determinar cuestiones externas e internas relevantes para su SGC.",
            },
            {
                "code": "4.2",
                "domain": "4. Contexto de la Organizacion",
                "title": "Comprension de las necesidades y expectativas de las partes interesadas",
                "description": "La organizacion debe identificar las partes interesadas relevantes para el SGC.",
            },
            {
                "code": "5.1",
                "domain": "5. Liderazgo",
                "title": "Liderazgo y compromiso",
                "description": "La alta direccion debe demostrar liderazgo y compromiso con el SGC.",
            },
            {
                "code": "5.2",
                "domain": "5. Liderazgo",
                "title": "Politica de calidad",
                "description": "La alta direccion debe establecer una politica de calidad apropiada.",
            },
            {
                "code": "5.3",
                "domain": "5. Liderazgo",
                "title": "Roles, responsabilidades e autoridades",
                "description": "La alta direccion debe asignar responsabilidades y autoridades.",
            },
            {
                "code": "6.1",
                "domain": "6. Planificacion",
                "title": "Acciones para abordar riesgos y oportunidades",
                "description": "La organizacion debe planificar acciones para abordar riesgos.",
            },
            {
                "code": "6.2",
                "domain": "6. Planificacion",
                "title": "Objetivos de calidad y planificación",
                "description": "La organizacion debe establecer objetivos de calidad.",
            },
            {
                "code": "7.1",
                "domain": "7. Apoyo",
                "title": "Recursos",
                "description": "La organizacion debe determinar y proporcionar recursos necesarios.",
            },
            {
                "code": "7.2",
                "domain": "7. Apoyo",
                "title": "Competencia",
                "description": "La organizacion debe asegurar que el personal sea competente.",
            },
            {
                "code": "7.3",
                "domain": "7. Apoyo",
                "title": "Toma de conciencia",
                "description": "El personal debe ser consciente de la politica y objetivos de calidad.",
            },
            {
                "code": "7.4",
                "domain": "7. Apoyo",
                "title": "Comunicacion",
                "description": "La organizacion debe determinar comunicaciones relevantes para el SGC.",
            },
            {
                "code": "7.5",
                "domain": "7. Apoyo",
                "title": "Informacion documentada",
                "description": "La organizacion debe crear y controlar informacion documentada.",
            },
            {
                "code": "8.1",
                "domain": "8. Operacion",
                "title": "Planificacion y control operacional",
                "description": "La organizacion debe planificar y controlar procesos operativos.",
            },
            {
                "code": "8.2",
                "domain": "8. Operacion",
                "title": "Requisitos de productos y servicios",
                "description": "La organizacion debe determinar requisitos de productos/servicios.",
            },
            {
                "code": "8.3",
                "domain": "8. Operacion",
                "title": "Diseno y desarrollo",
                "description": "La organizacion debe establecer procesos de diseno y desarrollo.",
            },
            {
                "code": "8.4",
                "domain": "8. Operacion",
                "title": "Control de procesos, productos y servicios externos",
                "description": "La organizacion debe controlar proveedores externos.",
            },
            {
                "code": "8.5",
                "domain": "8. Operacion",
                "title": "Produccion y provision del servicio",
                "description": "La organizacion debe controlar la produccion y provision de servicios.",
            },
            {
                "code": "8.6",
                "domain": "8. Operacion",
                "title": "Liberacion de productos y servicios",
                "description": "La organizacion debe liberar productos y servicios.",
            },
            {
                "code": "8.7",
                "domain": "8. Operacion",
                "title": "Control de salidas no conformes",
                "description": "La organizacion debe controlar salidas no conformes.",
            },
            {
                "code": "9.1",
                "domain": "9. Evaluacion del desempeno",
                "title": "Monitorizacion, medicion, analisis y evaluacion",
                "description": "La organizacion debe monitorear y medir procesos y productos.",
            },
            {
                "code": "9.2",
                "domain": "9. Evaluacion del desempeno",
                "title": "Auditoria interna",
                "description": "La organizacion debe realizar auditorias internas programadas.",
            },
            {
                "code": "9.3",
                "domain": "9. Evaluacion del desempeno",
                "title": "Revision por la direccion",
                "description": "La alta direccion debe revisar el SGC periodicamente.",
            },
            {
                "code": "10.1",
                "domain": "10. Mejora",
                "title": "Generalidades",
                "description": "La organizacion debe determinar oportunidades de mejora.",
            },
            {
                "code": "10.2",
                "domain": "10. Mejora",
                "title": "No conformidades y acciones correctivas",
                "description": "La organizacion debe tratar no conformidades y tomar acciones.",
            },
            {
                "code": "10.3",
                "domain": "10. Mejora",
                "title": "Mejora continua",
                "description": "La organizacion debe mejorar continuamente la adecuacion del SGC.",
            },
        ]
        for ctrl in iso9001_controls:
            ctrl["norma_id"] = normas_map["ISO9001"]
            session.add(ControlDefinition(**ctrl))

        iso20000_controls = [
            {
                "code": "4.1",
                "domain": "4. Sistema de Gestion",
                "title": "理解组织",
                "description": "La organizacion debe entender su contexto y necesidades.",
            },
            {
                "code": "4.2",
                "domain": "4. Sistema de Gestion",
                "title": "Comprension de necesidades de partes interesadas",
                "description": "La organizacion debe identificar partes interesadas y sus necesidades.",
            },
            {
                "code": "5.1",
                "domain": "5. Responsabilidad de la Direccion",
                "title": "Politica de SMS",
                "description": "La direccion debe establecer politica de gestion de servicios.",
            },
            {
                "code": "5.2",
                "domain": "5. Responsabilidad de la Direccion",
                "title": "Responsabilidades delegadas",
                "description": "La direccion debe definir responsabilidades claras.",
            },
            {
                "code": "6.1",
                "domain": "6. Gestion de Recursos",
                "title": "Recursos humanos",
                "description": "La organizacion debe definir competencias y gestionar personal.",
            },
            {
                "code": "6.2",
                "domain": "6. Gestion de Recursos",
                "title": "Competencias",
                "description": "El personal debe ser competente en base a educacion y experiencia.",
            },
            {
                "code": "7.1",
                "domain": "7. Procesos de Gestion de Servicios",
                "title": "Catalogo de servicios",
                "description": "La organizacion debe mantener un catalogo de servicios documentado.",
            },
            {
                "code": "7.2",
                "domain": "7. Procesos de Gestion de Servicios",
                "title": "Acuerdos de nivel de servicio (SLA)",
                "description": "La organizacion debe establecer y mantener SLAs.",
            },
            {
                "code": "7.3",
                "domain": "7. Procesos de Gestion de Servicios",
                "title": "Gestion de capacidad",
                "description": "La organizacion debe asegurar capacidad adecuada de servicios.",
            },
            {
                "code": "7.4",
                "domain": "7. Procesos de Gestion de Servicios",
                "title": "Gestion de continuidad",
                "description": "La organizacion debe mantener continuidad de servicios.",
            },
            {
                "code": "8.1",
                "domain": "8. Relacion con el Cliente",
                "title": "Acuerdos de servicio",
                "description": "La organizacion debe establecer acuerdos con clientes.",
            },
            {
                "code": "8.2",
                "domain": "8. Gestion de Incidentes",
                "title": "Proceso de gestion de incidentes",
                "description": "La organizacion debe tener proceso documentado de incidentes.",
            },
            {
                "code": "8.3",
                "domain": "8. Gestion de Problemas",
                "title": "Proceso de gestion de problemas",
                "description": "La organizacion debe gestionar problemas y sus causas raiz.",
            },
            {
                "code": "9.1",
                "domain": "9. Medicion y Mejora",
                "title": "Recopilacion y analisis de datos",
                "description": "La organizacion debe recopilar y analizar datos de servicios.",
            },
            {
                "code": "9.2",
                "domain": "9. Medicion y Mejora",
                "title": "Auditoria interna",
                "description": "La organizacion debe realizar auditorias internas.",
            },
            {
                "code": "9.3",
                "domain": "9. Medicion y Mejora",
                "title": "Revision del SMS",
                "description": "La direccion debe revisar el sistema de gestion de servicios.",
            },
        ]
        for ctrl in iso20000_controls:
            ctrl["norma_id"] = normas_map["ISO20000"]
            session.add(ControlDefinition(**ctrl))

        iso22301_controls = [
            {
                "code": "4.1",
                "domain": "4. Contexto",
                "title": "Comprension de la organizacion",
                "description": "La organizacion debe entender su contexto y requisitos legales.",
            },
            {
                "code": "4.2",
                "domain": "4. Contexto",
                "title": "Partes interesadas",
                "description": "La organizacion debe identificar partes interesadas en BCM.",
            },
            {
                "code": "5.1",
                "domain": "5. Liderazgo",
                "title": "Politica de continuidad",
                "description": "La direccion debe establecer politica de continuidad.",
            },
            {
                "code": "5.2",
                "domain": "5. Liderazgo",
                "title": "Roles y responsabilidades",
                "description": "La organizacion debe definir roles para BCM.",
            },
            {
                "code": "6.1",
                "domain": "6. Planificacion",
                "title": "Evaluacion de riesgos",
                "description": "La organizacion debe identificar y analizar riesgos.",
            },
            {
                "code": "6.2",
                "domain": "6. Planificacion",
                "title": "Determinacion de estrategias",
                "description": "La organizacion debe determinar estrategias de continuidad.",
            },
            {
                "code": "7.1",
                "domain": "7. Soporte",
                "title": "Recursos",
                "description": "La organizacion debe proporcionar recursos para BCM.",
            },
            {
                "code": "7.2",
                "domain": "7. Soporte",
                "title": "Competencia",
                "description": "El personal debe ser competente en continuidad.",
            },
            {
                "code": "7.3",
                "domain": "7. Soporte",
                "title": "Toma de conciencia",
                "description": "El personal debe entender sus responsabilidades en BCM.",
            },
            {
                "code": "8.1",
                "domain": "8. Operacion",
                "title": "Analisis de impacto (BIA)",
                "description": "La organizacion debe realizar analisis de impacto al negocio.",
            },
            {
                "code": "8.2",
                "domain": "8. Operacion",
                "title": "Evaluacion de riesgos",
                "description": "La organizacion debe evaluar riesgos de continuidad.",
            },
            {
                "code": "8.3",
                "domain": "8. Operacion",
                "title": "Estrategia de continuidad",
                "description": "La organizacion debe desarrollar estrategias de continuidad.",
            },
            {
                "code": "8.4",
                "domain": "8. Operacion",
                "title": "Plan de continuidad (BCP)",
                "description": "La organizacion debe establecer planes de continuidad.",
            },
            {
                "code": "8.5",
                "domain": "8. Operacion",
                "title": "Plan de recuperacion (DRP)",
                "description": "La organizacion debe establecer planes de recuperacion.",
            },
            {
                "code": "9.1",
                "domain": "9. Evaluacion",
                "title": "Ejercicios y pruebas",
                "description": "La organizacion debe probar los planes regularmente.",
            },
            {
                "code": "9.2",
                "domain": "9. Evaluacion",
                "title": "Revision por la direccion",
                "description": "La direccion debe revisar el sistema de BCM.",
            },
            {
                "code": "10.1",
                "domain": "10. Mejora",
                "title": "Mejora continua",
                "description": "La organizacion debe mejorar continuamente el BCM.",
            },
        ]
        for ctrl in iso22301_controls:
            ctrl["norma_id"] = normas_map["ISO22301"]
            session.add(ControlDefinition(**ctrl))

        # ITIL v4 Practices
        itil4_controls = [
            # General
            {
                "code": "ITSV-1",
                "domain": "SVS - Service Value System",
                "title": "Service Value System",
                "description": "El SVS determina como los recursos se transforman en valor a traves de actividades y gobernanza.",
            },
            {
                "code": "ITSV-2",
                "domain": "4 Dimensions Model",
                "title": "Four Dimensions of Service Value",
                "description": "Las cuatro dimensiones que deben estar balanceadas para la creacion de valor.",
            },
            # Governance
            {
                "code": "GOV-1",
                "domain": "Governance - Direct",
                "title": "Direct and Justify",
                "description": "Direccionar y justificar las politicas, regulaciones y estrategas de la organizacion.",
            },
            {
                "code": "GOV-2",
                "domain": "Governance - Plan",
                "title": "Plan and Set Direction",
                "description": "Planificar y establecer la direccion estrategica y tactica de la organizacion.",
            },
            {
                "code": "GOV-3",
                "domain": "Governance - Improve",
                "title": "Improve and Achieve Objectives",
                "description": "Mejorar continuamente y lograr los objetivos de la organizacion.",
            },
            # Value Streams
            {
                "code": "VST-1",
                "domain": "Value Streams and Pathways",
                "title": "Design and Engineer",
                "description": "Disenar e ingenierar servicios para crear valor.",
            },
            {
                "code": "VST-2",
                "domain": "Value Streams and Pathways",
                "title": "Deliver and Support",
                "description": "Entregar y soportar servicios para generar valor.",
            },
            # Operational Practices
            {
                "code": "OPE-1",
                "domain": "Operating Model",
                "title": "Change Enablement",
                "description": "Maximizar la probabilidad de resultados exitosos de cambios changeEnablementng.",
            },
            {
                "code": "OPE-2",
                "domain": "Operating Model",
                "title": "Incident Management",
                "description": "Minimizar el impacto negativo de incidentes restaurando el servicio normal.",
            },
            {
                "code": "OPE-3",
                "domain": "Operating Model",
                "title": "Problem Management",
                "description": "Reducir la probabilidad e impacto de incidentes eliminando errores.",
            },
            {
                "code": "OPE-4",
                "domain": "Operating Model",
                "title": "Service Request Management",
                "description": "Soportar la carga de trabajo predefinida y auto-servicio.",
            },
            {
                "code": "OPE-5",
                "domain": "Operating Model",
                "title": "IT Asset Management",
                "description": "Planificar y gestionar el ciclo de vida de los activos de TI.",
            },
            # Improvement
            {
                "code": "IMP-1",
                "domain": "Improvement - Continual",
                "title": "Continual Improvement",
                "description": "Alinear las practicas de mejora con las necesidades actuales y futuras.",
            },
            {
                "code": "IMP-2",
                "domain": "Improvement - Measurement",
                "title": "Measurement and Reporting",
                "description": "Definir y capturar metricas para demostrar valor y mejora.",
            },
            # Relationships
            {
                "code": "REL-1",
                "domain": "Relationships",
                "title": "Business Analysis",
                "description": "Identificar necesidades y oportunidades de negocio.",
            },
            {
                "code": "REL-2",
                "domain": "Relationships",
                "title": "Portfolio Management",
                "description": "Gestionar portafolio de servicios, productos y recursos.",
            },
            {
                "code": "REL-3",
                "domain": "Relationships",
                "title": "Relationship Management",
                "description": "Fomentar relaciones positivas y trabajar con stakeholders.",
            },
            # Supply
            {
                "code": "SUP-1",
                "domain": "Supply and Demand",
                "title": "Supplier Management",
                "description": "Asegurar que los proveedores deliversn valor sostenible.",
            },
            {
                "code": "SUP-2",
                "domain": "Supply and Demand",
                "title": "Service Level Management",
                "description": "Establecer y mantener acuerdos de nivel de servicio.",
            },
            {
                "code": "SUP-3",
                "domain": "Supply and Demand",
                "title": "Service Configuration",
                "description": "Asegurar informacion akuratica de configuracion de servicios.",
            },
            # Technical
            {
                "code": "TEC-1",
                "domain": "Technical Practices",
                "title": "Deployment Management",
                "description": "Mover servicios nuevos o modificados a produccion.",
            },
            {
                "code": "TEC-2",
                "domain": "Technical Practices",
                "title": "Infrastructure and Platform",
                "description": "Gestionar infraestructura y plataformas de servicios.",
            },
            {
                "code": "TEC-3",
                "domain": "Technical Practices",
                "title": "Software Development",
                "description": "Desarrollar y mantener software de servicios.",
            },
            {
                "code": "TEC-4",
                "domain": "Technical Practices",
                "title": "Security Management",
                "description": "Proteger la informacion y los datos de la organizacion.",
            },
            # Service Value Chain
            {
                "code": "SVC-1",
                "domain": "Service Value Chain",
                "title": "Engage and Plan",
                "description": "Proveer vision clara, retroalimentacion y mejora continua.",
            },
            {
                "code": "SVC-2",
                "domain": "Service Value Chain",
                "title": "Design and Transition",
                "description": "Diseñar y desarrollar nuevos servicios y caracteristicas.",
            },
            {
                "code": "SVC-3",
                "domain": "Service Value Chain",
                "title": "Obtain and Build",
                "description": "Asegurar que componentes de servicio esten disponibles.",
            },
            {
                "code": "SVC-4",
                "domain": "Service Value Chain",
                "title": "Deliver and Support",
                "description": "Entregar servicios de acuerdo a especificaciones.",
            },
            # Additional ITIL Practices
            {
                "code": "ADD-1",
                "domain": "Organization and People",
                "title": "Organizational Change Management",
                "description": "Preparar a personas para cambios organizacionales.",
            },
            {
                "code": "ADD-2",
                "domain": "Organization and People",
                "title": "Workforce and Talent Management",
                "description": "Desarrollar capacidades y competencias del personal.",
            },
            {
                "code": "ADD-3",
                "domain": "Information and Technology",
                "title": "Information Security Management",
                "description": "Proteger la informacion mediante controles de seguridad.",
            },
            {
                "code": "ADD-4",
                "domain": "Information and Technology",
                "title": "Knowledge Management",
                "description": "Mantener y mejorar el conocimiento organizacional.",
            },
            {
                "code": "ADD-5",
                "domain": "Partners and Suppliers",
                "title": "Vendor Assessment",
                "description": "Evaluar capacidades y riesgos de proveedores.",
            },
        ]

            itil4_norma = session.exec(select(Norma).where(Norma.code == "ITIL4")).first()
            if itil4_norma:
                try:
                    itil_controls = session.exec(
                        select(ControlDefinition).where(
                            ControlDefinition.norma_id == itil4_norma.id
                        )
                    ).first()
                    if not itil_controls:
                        for ctrl in itil4_controls:
                            ctrl["norma_id"] = itil4_norma.id
                            session.add(ControlDefinition(**ctrl))
                        print(f"  Agregados {len(itil4_controls)} controles ITIL v4")
                except Exception as e:
                    print(f"  Error ITIL4: {e}")
                    session.rollback()

        existing_client = session.exec(
            select(Client).where(Client.name == "Cliente Demo")
        ).first()
        if not existing_client:
            default_client = Client(name="Cliente Demo", sector="General")
            session.add(default_client)
            session.flush()
        else:
            default_client = existing_client

        existing_superadmin = session.exec(
            select(User).where(User.email == "admin@iso27001.local")
        ).first()
        if not existing_superadmin:
            superadmin = User(
                email="admin@iso27001.local",
                password_hash=hash_password("admin123"),
                name="Super Administrador",
                role=UserRole.SUPERADMIN,
                client_id=None,
            )
            session.add(superadmin)

        existing_admin_demo = session.exec(
            select(User).where(User.email == "admin@demo.local")
        ).first()
        if not existing_admin_demo:
            admin_demo = User(
                email="admin@demo.local",
                password_hash=hash_password("demo123"),
                name="Administrador Demo",
                role=UserRole.ADMIN_CLIENTE,
                client_id=default_client.id,
            )
            session.add(admin_demo)

        session.commit()
        print("Seed completado. Usuarios creados:")
        print("  Superadmin: admin@iso27001.local / admin123")
        print("  Admin Demo: admin@demo.local / demo123")
