import React from 'react';
import './learner-rewards.css';

type Rewards = {id:number;xp:number;level:number;xp_per_level:number;level_progress:number;next_level:number;xp_until_next_level:number};

function validRewards(user:Partial<Rewards>|null|undefined,learnerId:number):user is Rewards{
  if(!user||user.id!==learnerId)return false;
  const values=[user.xp,user.level,user.xp_per_level,user.level_progress,user.next_level,user.xp_until_next_level];
  if(!values.every(value=>Number.isInteger(value)))return false;
  const data=user as Rewards;
  return data.xp>=0&&data.level>=1&&data.xp_per_level>0&&data.level_progress>=0&&data.level_progress<data.xp_per_level&&
    data.next_level===data.level+1&&data.xp_until_next_level>0&&data.level_progress+data.xp_until_next_level===data.xp_per_level;
}

export function LearnerRewards({learnerId,user}:{learnerId:number;user?:Partial<Rewards>|null}){
  if(!validRewards(user,learnerId))return <p className="learner-rewards-unavailable" role="status">Your level and XP are currently unavailable.</p>;
  const rewards=user;
  const percent=Math.round(rewards.level_progress/rewards.xp_per_level*100);
  return <section className="learner-rewards" aria-label="Your level and XP">
    <div className="learner-rewards-values"><strong>Level {rewards.level}</strong><span>{rewards.xp.toLocaleString('en-AU')} XP</span></div>
    <div role="progressbar" aria-label={`Progress towards Level ${rewards.next_level}`} aria-valuemin={0} aria-valuemax={rewards.xp_per_level} aria-valuenow={rewards.level_progress} aria-valuetext={`${percent} percent, ${rewards.xp_until_next_level} XP until Level ${rewards.next_level}`} className="learner-rewards-track"><i style={{width:`${percent}%`}}/></div>
    <small>{rewards.xp_until_next_level} XP until Level {rewards.next_level}</small>
  </section>;
}
