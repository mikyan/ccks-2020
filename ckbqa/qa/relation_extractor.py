# -*- coding: utf-8 -*-
import logging

from ckbqa.qa.neo4j_graph import GraphDB
from ckbqa.utils.decorators import singleton


@singleton
class RelationExtractor(object):

    def __init__(self):
        self.graph_db = GraphDB()
        # self.sim_predictor = RelationScorePredictor(model_name='bert_match')  # bert_match,bert_match2

    def get_relations(self, candidate_entities, ent_name, direction='out'):
        onehop_relations = self.graph_db.get_onehop_relations_by_entName(ent_name, direction=direction)
        twohop_relations = self.graph_db.get_twohop_relations_by_entName(ent_name, direction=direction)
        mention = candidate_entities[ent_name]['mention']
        candidate_paths, candidate_sents = [], []
        for rel_name in onehop_relations:
            _candidate_path = '的'.join([mention, rel_name[1:-1]])  # 查询的关系有<>,需要去掉
            candidate_sents.append(_candidate_path)
            candidate_paths.append([ent_name, rel_name])
        for rels in twohop_relations:
            pure_rel_names = [rel_name[1:-1] for rel_name in rels]  # python-list 关系名列表
            _candidate_path = '的'.join([mention] + pure_rel_names)
            candidate_sents.append(_candidate_path)
            candidate_paths.append([ent_name] + rels)
        return candidate_paths, candidate_sents

    def get_ent_relations(self, q_text, candidate_entities):
        """
        :param q_text:
        :param candidate_entities: {ent:[mention, feature1, feature2, ...]}
        :return:
        """
        candidate_out_sents, candidate_out_paths = [], []
        candidate_in_sents, candidate_in_paths = [], []
        for entity in candidate_entities:
            candidate_paths, candidate_sents = self.get_relations(candidate_entities, entity, direction='out')
            candidate_out_sents.extend(candidate_sents)
            candidate_out_paths.extend(candidate_paths)
            candidate_paths, candidate_sents = self.get_relations(candidate_entities, entity, direction='in')
            candidate_in_sents.extend(candidate_sents)
            candidate_in_paths.extend(candidate_paths)
        if not candidate_out_sents and not candidate_in_sents:
            logging.info('* candidate_out_paths Empty ...')
            return
        # sim_scores = self.sim_predictor.predict(q_text, candidate_out_paths) #目前算法不好，score==1
        return candidate_out_paths, candidate_in_paths

    def relation_score_topn(self):
        pass
