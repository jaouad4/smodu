import { CheckCircleFilled, MinusCircleOutlined } from '@ant-design/icons';
import { Card, Col, Empty, Row, Skeleton, Tag, Typography } from 'antd';
import { useQuery } from '@tanstack/react-query';
import { competencesApi } from '@/api/competences';
import type { Level } from '@/types';

const { Title, Text } = Typography;

const levelColor: Record<Level, string> = {
  DISCOVERY: '#bab9b4',
  BEGINNER: '#006494',
  INTERMEDIATE: '#da7101',
  AUTONOMOUS: '#7a39bb',
  PROJECT_READY: '#01696f',
};

const levelLabel: Record<Level, string> = {
  DISCOVERY: 'Découverte',
  BEGINNER: 'Débutant',
  INTERMEDIATE: 'Intermédiaire',
  AUTONOMOUS: 'Autonome',
  PROJECT_READY: 'Prêt Projet',
};

const CompetencesPage = () => {
  const { data: matrix, isLoading } = useQuery({
    queryKey: ['competences', 'matrix'],
    queryFn: competencesApi.getMyMatrix,
  });

  if (isLoading) return <Skeleton active paragraph={{ rows: 10 }} />;
  if (!matrix || !matrix.skills.length) return <Empty description="Aucune compétence enregistrée" />;

  // Grouper par domaine
  const byDomain = matrix.skills.reduce<Record<string, typeof matrix.skills>>((acc, us) => {
    const domain = us.skill.domain.name;
    if (!acc[domain]) acc[domain] = [];
    acc[domain].push(us);
    return acc;
  }, {});

  return (
    <div>
      <Title level={2}>Ma Matrice de Compétences</Title>
      <Text type="secondary" style={{ display: 'block', marginBottom: 32 }}>
        Compétences validées par domaine fonctionnel Odoo
      </Text>

      {Object.entries(byDomain).map(([domain, skills]) => (
        <Card
          key={domain}
          title={<Text strong style={{ fontSize: 16 }}>{domain}</Text>}
          style={{ marginBottom: 24 }}
        >
          <Row gutter={[12, 12]}>
            {skills.map(us => (
              <Col xs={24} sm={12} md={8} key={us.skill.id}>
                <Card
                  size="small"
                  style={{
                    borderLeft: `4px solid ${levelColor[us.level]}`,
                    borderRadius: 6,
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <Text strong style={{ fontSize: 13 }}>{us.skill.name}</Text>
                    {us.is_validated
                      ? <CheckCircleFilled style={{ color: '#01696f' }} />
                      : <MinusCircleOutlined style={{ color: '#bab9b4' }} />
                    }
                  </div>
                  <Tag
                    color={levelColor[us.level]}
                    style={{ marginTop: 8, fontSize: 11 }}
                  >
                    {levelLabel[us.level]}
                  </Tag>
                  {us.validated_by && (
                    <Text type="secondary" style={{ fontSize: 11, display: 'block', marginTop: 4 }}>
                      Validé par {us.validated_by}
                    </Text>
                  )}
                </Card>
              </Col>
            ))}
          </Row>
        </Card>
      ))}
    </div>
  );
};

export default CompetencesPage;
