import json
import os

import pytest

from camelgym.logs import logger
from camelgym.const import WORKSPACE_ROOT
from werewolf_game.schema import RoleExperience
from werewolf_game.actions.experience_operation import AddNewExperiences, RetrieveExperiences


class TestExperiencesOperation:

    collection_name = "test"
    test_round_id = "test_01"
    version = "test"
    samples_to_add = [
        RoleExperience(profile="Witch", reflection="The game is intense with two players claiming to be the Witch and one claiming to be the Seer. Player4's behavior is suspicious.", response="", outcome="", round_id=test_round_id, version=version),
        RoleExperience(profile="Witch", reflection="The game is in a critical state with only three players left, and I need to make a wise decision to save Player7 or not.", response="", outcome="", round_id=test_round_id, version=version),
        RoleExperience(profile="Seer", reflection="Player1, who is a werewolf, falsely claimed to be a Seer, and Player6, who might be a Witch, sided with him. I, as the real Seer, am under suspicion.", response="", outcome="", round_id=test_round_id, version=version),
        RoleExperience(profile="TestRole", reflection="Some test reflection1", response="", outcome="", round_id=test_round_id, version=version+"_01-10"),
        RoleExperience(profile="TestRole", reflection="Some test reflection2", response="", outcome="", round_id=test_round_id, version=version+"_11-20"),
        RoleExperience(profile="TestRole", reflection="Some test reflection3", response="", outcome="", round_id=test_round_id, version=version+"_21-30"),
    ]

    @pytest.mark.asyncio
    async def test_add(self):
        saved_file = f"{WORKSPACE_ROOT}/werewolf_game/experiences/{self.version}/{self.test_round_id}.json"
        if os.path.exists(saved_file):
            os.remove(saved_file)

        action = AddNewExperiences(collection_name=self.collection_name, delete_existing=True)
        action.run(self.samples_to_add)
        
        # test insertion
        inserted = action.collection.get()
        assert len(inserted["documents"]) == len(self.samples_to_add)

        # test if we record the samples correctly to local file
        # & test if we could recover a embedding db from the file
        action = AddNewExperiences(collection_name=self.collection_name, delete_existing=True)
        action.add_from_file(saved_file)
        inserted = action.collection.get()
        assert len(inserted["documents"]) == len(self.samples_to_add)

    @pytest.mark.asyncio
    async def test_retrieve(self):
        action = RetrieveExperiences(collection_name=self.collection_name)

        query = "one player claimed to be Seer and the other Witch"
        results = action.run(query, profile="Witch")
        results = json.loads(results)

        assert len(results) == 2, "Witch should have 2 experiences"
        assert "The game is intense with two players" in results[0]
    
    @pytest.mark.asyncio
    async def test_retrieve_filtering(self):
        action = RetrieveExperiences(collection_name=self.collection_name)

        query = "some test query"
        profile = "TestRole"
        
        excluded_version = ""
        results = action.run(query, profile=profile, excluded_version=excluded_version)
        results = json.loads(results)
        assert len(results) == 3
        
        excluded_version = self.version + "_21-30"
        results = action.run(query, profile=profile, excluded_version=excluded_version)
        results = json.loads(results)
        assert len(results) == 2

class TestActualRetrieve:

    collection_name = "role_reflection"

    @pytest.mark.asyncio
    async def test_check_experience_pool(self):
        logger.info("check experience pool")
        action = RetrieveExperiences(collection_name=self.collection_name)
        all_experiences = action.collection.get()
        logger.info(f"{len(all_experiences['metadatas'])=}")
        print(*["metadatas"][-5:], sep="\n")

    @pytest.mark.asyncio
    async def test_retrieve_werewolf_experience(self):
        
        action = RetrieveExperiences(collection_name=self.collection_name)

        query = "there are conflicts"

        logger.info(f"test retrieval with {query=}")
        results = action.run(query, "Werewolf")
    
    @pytest.mark.asyncio
    async def test_retrieve_villager_experience(self):
        
        action = RetrieveExperiences(collection_name=self.collection_name)

        query = "there are conflicts"

        logger.info(f"test retrieval with {query=}")
        results = action.run(query, "Seer")
        assert "conflict" in results # 相似局面应该需要包含conflict关键词
    
    @pytest.mark.asyncio
    async def test_retrieve_villager_experience_filtering(self):
        
        action = RetrieveExperiences(collection_name=self.collection_name)

        query = "there are conflicts"

        excluded_version = "01-10"
        logger.info(f"test retrieval with {excluded_version=}")
        results_01_10 = action.run(query, profile="Seer", excluded_version=excluded_version, verbose=True)
        
        excluded_version = "11-20"
        logger.info(f"test retrieval with {excluded_version=}")
        results_11_20 = action.run(query, profile="Seer", excluded_version=excluded_version, verbose=True)

        assert results_01_10 != results_11_20
